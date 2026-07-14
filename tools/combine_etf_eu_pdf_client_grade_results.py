from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"missing PDF gate artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Combine Dutch and English ETF EU PDF machine-gate artifacts.")
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--repair-run-id", required=True)
    parser.add_argument("--dutch", required=True)
    parser.add_argument("--english", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    dutch_path = Path(args.dutch)
    english_path = Path(args.english)
    dutch = _load(dutch_path)
    english = _load(english_path)
    blockers = list(dutch.get("blockers") or []) + list(english.get("blockers") or [])
    payload = {
        "schema_version": "etf_eu_routine_pdf_client_grade_combined_v2",
        "artifact_type": "etf_eu_routine_pdf_client_grade_combined",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_run_id": args.source_run_id,
        "repair_run_id": args.repair_run_id,
        "dutch_artifact": str(dutch_path),
        "english_artifact": str(english_path),
        "dutch_pdf_client_grade_passed": dutch.get("machine_validation_passed") is True,
        "english_pdf_client_grade_passed": english.get("machine_validation_passed") is True,
        "client_surface_clean": dutch.get("client_surface_clean") is True and english.get("client_surface_clean") is True,
        "authority_metadata_absent": dutch.get("authority_metadata_absent") is True and english.get("authority_metadata_absent") is True,
        "raw_status_enums_absent": dutch.get("raw_status_enums_absent") is True and english.get("raw_status_enums_absent") is True,
        "pdf_client_grade_passed": dutch.get("machine_validation_passed") is True and english.get("machine_validation_passed") is True and not blockers,
        "blockers": blockers,
        "warnings": list(dutch.get("warnings") or []) + list(english.get("warnings") or []),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["pdf_client_grade_passed"] is not True:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
