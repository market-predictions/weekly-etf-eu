from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_validator(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "passed": completed.returncode == 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run activated-state allocator-report validation bundle")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    validators = [
        "tools/validate_etf_eu_activated_report_surface.py",
        "tools/validate_etf_eu_incumbent_overlap_surface.py",
        "tools/validate_etf_eu_promoted_candidate_visibility.py",
        "tools/validate_etf_eu_policy_report_pagination.py",
        "tools/validate_etf_eu_sister_report_pdf_layout.py",
        "tools/validate_etf_eu_sister_report_shadow.py",
        "tools/validate_etf_eu_donor_surface_contract.py",
    ]
    results = [run_validator([sys.executable, validator, str(args.manifest)]) for validator in validators]
    payload = {
        "schema_version": "etf_eu_allocator_report_validation_bundle_v10",
        "artifact_type": "etf_eu_allocator_report_validation_bundle",
        "validation_mode": "activated_l0ck_remaining_vvsm_monitor",
        "generated_at_utc": utc_now(),
        "manifest": str(args.manifest),
        "valid": all(result["passed"] for result in results),
        "results": results,
        "funded_stage1_tickers": ["L0CK"],
        "remaining_monitored_tickers": ["VVSM"],
        "current_position_count": 4,
        "portfolio_mutation": False,
        "funding_authority": False,
        "execution_authority": False,
        "real_broker_execution": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if not payload["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
