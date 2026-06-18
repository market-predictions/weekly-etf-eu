from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_delivery_pdf_dry_run_v1"
FALSE_FLAGS = [
    "production_delivery",
    "recipient_activation",
    "send_attempted",
    "mail_transport_enabled",
    "smtp_configured",
    "secrets_present",
    "real_recipients",
    "real_receipt",
    "proof_claimed",
    "portfolio_mutation",
    "candidate_promotion",
    "funding_authority",
    "valuation_grade",
]
REQUIRED_FIELDS = {
    "schema_version",
    "run_id",
    "status",
    "created_at_utc",
    "report_path",
    "pricing_artifact_path",
    "porting_artifact_path",
    "bilingual_surface_artifact_path",
    "dry_run_only",
    "pdf_generation_status",
    "html_generation_status",
    "validators_run",
    "tests_expected",
    "selected_next_package",
    "selected_next_package_title",
    *FALSE_FLAGS,
}


class EtfEuDeliveryPdfDryRunError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EtfEuDeliveryPdfDryRunError("artifact root must be object")
    return payload


def _path_must_exist(payload: dict[str, Any], key: str) -> None:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuDeliveryPdfDryRunError(f"{key} missing")
    if not Path(raw).exists():
        raise EtfEuDeliveryPdfDryRunError(f"{key} does not exist: {raw}")


def validate_delivery_pdf_dry_run(path: Path) -> dict[str, str]:
    payload = _load(path)
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        raise EtfEuDeliveryPdfDryRunError("missing fields: " + ", ".join(missing))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuDeliveryPdfDryRunError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuDeliveryPdfDryRunError("status must be completed")
    if payload.get("dry_run_only") is not True:
        raise EtfEuDeliveryPdfDryRunError("dry_run_only must be true")
    for key in FALSE_FLAGS:
        if payload.get(key) is not False:
            raise EtfEuDeliveryPdfDryRunError(f"{key} must be false")
    for key in ("report_path", "pricing_artifact_path", "porting_artifact_path", "bilingual_surface_artifact_path"):
        _path_must_exist(payload, key)
    if not isinstance(payload.get("validators_run"), list) or not payload["validators_run"]:
        raise EtfEuDeliveryPdfDryRunError("validators_run must be non-empty list")
    if not isinstance(payload.get("tests_expected"), list) or not payload["tests_expected"]:
        raise EtfEuDeliveryPdfDryRunError("tests_expected must be non-empty list")
    if not str(payload.get("selected_next_package") or "").strip():
        raise EtfEuDeliveryPdfDryRunError("selected_next_package missing")
    print(f"ETF_EU_DELIVERY_PDF_DRY_RUN_OK | artifact={path} | selected_next_package={payload['selected_next_package']}")
    return {"status": "valid", "artifact": str(path), "selected_next_package": str(payload["selected_next_package"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_delivery_pdf_dry_run(Path(args.artifact))


if __name__ == "__main__":
    main()
