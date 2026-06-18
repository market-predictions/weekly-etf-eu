from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_html_pdf_render_dry_run_v1"
FALSE_FIELDS = [
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
    "english_markdown_report_path",
    "dutch_markdown_report_path",
    "english_html_output_path",
    "dutch_html_output_path",
    "bilingual_surface_artifact_path",
    "previous_delivery_dry_run_artifact_path",
    "dry_run_only",
    "html_generation_status",
    "pdf_generation_status",
    "validators_run",
    "tests_expected",
    "selected_next_package",
    "selected_next_package_title",
    *FALSE_FIELDS,
}

FORBIDDEN_HTML_PATTERNS = [
    re.compile(r"<script\b", re.IGNORECASE),
    re.compile(r"mailto:", re.IGNORECASE),
    re.compile(r"tracking[-_ ]?pixel", re.IGNORECASE),
    re.compile(r"recipient@example", re.IGNORECASE),
    re.compile(r"smtp[_:\-]", re.IGNORECASE),
    re.compile(r"secret[_:\-]", re.IGNORECASE),
]


class EtfEuHtmlPdfDryRunError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise EtfEuHtmlPdfDryRunError("manifest root must be object")
    return payload


def _path(payload: dict[str, Any], key: str) -> Path:
    raw = str(payload.get(key) or "").strip()
    if not raw:
        raise EtfEuHtmlPdfDryRunError(f"{key} missing")
    path = Path(raw)
    if not path.exists():
        raise EtfEuHtmlPdfDryRunError(f"{key} does not exist: {raw}")
    return path


def _validate_html(path: Path, *, language: str) -> None:
    text = path.read_text(encoding="utf-8")
    for pattern in FORBIDDEN_HTML_PATTERNS:
        if pattern.search(text):
            raise EtfEuHtmlPdfDryRunError(f"forbidden HTML pattern in {path}: {pattern.pattern}")
    for marker in ["dry_run_only=true", "production_delivery=false", "recipient_activation=false", "send_attempted=false", "real_receipt=false"]:
        if marker not in text:
            raise EtfEuHtmlPdfDryRunError(f"HTML missing dry-run marker {marker}: {path}")
    for marker in ["UCITS", "CSPX.L", "SXR8.DE"]:
        if marker not in text:
            raise EtfEuHtmlPdfDryRunError(f"HTML missing {marker}: {path}")
    if language == "en" and "U.S. ETFs are research proxies only" not in text:
        raise EtfEuHtmlPdfDryRunError("English HTML missing proxy separation")
    if language == "nl" and "Amerikaanse ETF's zijn alleen researchproxy" not in text:
        raise EtfEuHtmlPdfDryRunError("Dutch HTML missing proxy separation")


def validate_html_pdf_dry_run(path: Path) -> dict[str, str]:
    payload = _load(path)
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        raise EtfEuHtmlPdfDryRunError("missing fields: " + ", ".join(missing))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EtfEuHtmlPdfDryRunError("bad schema_version")
    if payload.get("status") != "completed":
        raise EtfEuHtmlPdfDryRunError("status must be completed")
    if payload.get("dry_run_only") is not True:
        raise EtfEuHtmlPdfDryRunError("dry_run_only must be true")
    for key in FALSE_FIELDS:
        if payload.get(key) is not False:
            raise EtfEuHtmlPdfDryRunError(f"{key} must be false")
    en_html = _path(payload, "english_html_output_path")
    nl_html = _path(payload, "dutch_html_output_path")
    for key in ("english_markdown_report_path", "dutch_markdown_report_path", "bilingual_surface_artifact_path", "previous_delivery_dry_run_artifact_path"):
        _path(payload, key)
    _validate_html(en_html, language="en")
    _validate_html(nl_html, language="nl")
    if not str(payload.get("selected_next_package") or "").strip():
        raise EtfEuHtmlPdfDryRunError("selected_next_package missing")
    print(f"ETF_EU_HTML_PDF_DRY_RUN_OK | artifact={path} | selected_next_package={payload['selected_next_package']}")
    return {"status": "valid", "artifact": str(path), "selected_next_package": str(payload["selected_next_package"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    validate_html_pdf_dry_run(Path(args.artifact))


if __name__ == "__main__":
    main()
