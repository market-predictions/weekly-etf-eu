from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_shadow_pdf_manifest_v1"
DEFAULT_OUTPUT_DIR = Path("output/pdf")
FALSE_AUTHORITY_FLAGS = [
    "production_delivery",
    "email_delivery",
    "delivery_receipt",
    "portfolio_mutation",
    "funding_authority",
    "valuation_grade",
    "candidate_promotion",
    "workflow_integrated",
]
REQUIRED_ARTIFACT_KINDS = {"dutch_primary_shadow_pdf", "english_companion_shadow_pdf"}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_manifest(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("etf_eu_shadow_pdf_manifest_*.json"))
    if not files:
        raise RuntimeError(f"No ETF EU shadow PDF manifest found in {output_dir}")
    return files[-1]


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _validate_pdf(path: Path, output_dir: Path, errors: list[str], label: str) -> None:
    if path.suffix.lower() != ".pdf":
        errors.append(f"{label}:must_have_pdf_suffix")
    if not _is_relative_to(path, output_dir):
        errors.append(f"{label}:must_be_inside_output_pdf_dir")
    if not path.exists():
        errors.append(f"{label}:missing_pdf_file:{path}")
        return
    if path.stat().st_size <= 0:
        errors.append(f"{label}:pdf_must_be_non_empty")
    if not path.read_bytes().startswith(b"%PDF-"):
        errors.append(f"{label}:pdf_header_missing")


def validate(manifest_path: Path, *, output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    payload = _load_json(manifest_path)
    errors: list[str] = []

    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_must_be_etf_eu_shadow_pdf_manifest_v1")
    if payload.get("artifact_type") != "shadow_pdf_manifest":
        errors.append("artifact_type_must_be_shadow_pdf_manifest")
    if payload.get("status") != "shadow_only":
        errors.append("status_must_be_shadow_only")
    if payload.get("pdf_generation") != "shadow_only":
        errors.append("pdf_generation_must_be_shadow_only")
    if not _text(payload.get("run_id")):
        errors.append("run_id_required")
    if not _text(payload.get("report_date")):
        errors.append("report_date_required")
    for flag in FALSE_AUTHORITY_FLAGS:
        if payload.get(flag) is not False:
            errors.append(f"{flag}_must_be_false")
    for flag in ["not_delivery_receipt", "shadow_artifacts_only"]:
        if payload.get(flag) is not True:
            errors.append(f"{flag}_must_be_true")

    dutch_pdf = Path(_text(payload.get("dutch_pdf_path")))
    english_pdf = Path(_text(payload.get("english_pdf_path")))
    if not dutch_pdf.name.startswith("weekly_etf_eu_review_nl_"):
        errors.append("dutch_pdf_name_must_match_weekly_etf_eu_review_nl")
    if not english_pdf.name.startswith("weekly_etf_eu_review_") or english_pdf.name.startswith("weekly_etf_eu_review_nl_"):
        errors.append("english_pdf_name_must_match_weekly_etf_eu_review")
    _validate_pdf(dutch_pdf, output_dir, errors, "dutch_pdf")
    _validate_pdf(english_pdf, output_dir, errors, "english_pdf")

    artifacts = payload.get("artifacts") or []
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifacts_must_be_non_empty_list")
    else:
        kinds = {_text(item.get("kind")) for item in artifacts if isinstance(item, dict)}
        missing = REQUIRED_ARTIFACT_KINDS - kinds
        if missing:
            errors.append("missing_artifact_kinds:" + ",".join(sorted(missing)))
        for index, item in enumerate(artifacts):
            label = f"artifact:{index}"
            if not isinstance(item, dict):
                errors.append(f"{label}:must_be_object")
                continue
            if item.get("exists") is not True:
                errors.append(f"{label}:exists_must_be_true")
            if int(item.get("size_bytes") or 0) <= 0:
                errors.append(f"{label}:size_bytes_must_be_positive")
            if len(_text(item.get("sha256"))) != 64:
                errors.append(f"{label}:sha256_must_be_64_hex_chars")
            source = Path(_text(item.get("source_markdown_path")))
            if source.suffix.lower() != ".md":
                errors.append(f"{label}:source_markdown_must_have_md_suffix")

    if errors:
        raise RuntimeError("ETF EU shadow PDF validation failed: " + "; ".join(errors))
    print(
        "ETF_EU_SHADOW_PDF_VALIDATION_OK"
        f" | manifest={manifest_path}"
        " | pdf_generation=shadow_only | production_delivery=false | email_delivery=false | delivery_receipt=false"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    manifest = Path(args.artifact) if args.artifact else latest_manifest(output_dir)
    validate(manifest, output_dir=output_dir)


if __name__ == "__main__":
    main()
