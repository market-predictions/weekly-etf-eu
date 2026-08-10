from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCHEMA = "etf_eu_guarded_delivery_authority_v1"
ARTIFACT_TYPE = "etf_eu_guarded_delivery_authority"
PRODUCT = "weekly_etf_eu"
REQUIRED_ARTIFACT_KEYS = (
    "nl_md",
    "en_md",
    "nl_html",
    "en_html",
    "nl_pdf",
    "en_pdf",
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _normalise_hash(value: str) -> str:
    return value if value.startswith("sha256:") else "sha256:" + value


def _load(path: Path) -> dict[str, Any]:
    _require(path.exists(), f"delivery authority missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(payload, dict), "delivery authority must be a JSON object")
    return payload


def validate(path: Path) -> dict[str, Any]:
    payload = _load(path)
    _require(payload.get("schema_version") == SCHEMA, "delivery authority schema mismatch")
    _require(payload.get("artifact_type") == ARTIFACT_TYPE, "delivery authority type mismatch")
    _require(payload.get("product") == PRODUCT, "delivery authority product mismatch")
    _require(payload.get("status") == "APPROVED_FOR_GUARDED_DELIVERY", "delivery is not approved")
    _require(payload.get("delivery_authority") is True, "delivery_authority must be true")
    _require(payload.get("portfolio_mutation") is False, "delivery authority cannot mutate portfolio")
    _require(payload.get("broker_execution") is False, "delivery authority cannot authorize broker execution")

    report_date = str(payload.get("report_date", ""))
    report_suffix = str(payload.get("report_suffix", ""))
    report_run_id = str(payload.get("report_run_id", ""))
    _require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_date) is not None, "invalid report_date")
    _require(re.fullmatch(r"\d{6}", report_suffix) is not None, "invalid report_suffix")
    _require(report_date[2:4] + report_date[5:7] + report_date[8:10] == report_suffix, "report suffix/date mismatch")
    _require(re.fullmatch(r"\d{8}_\d{6}", report_run_id) is not None, "invalid report_run_id")
    _require(report_run_id[:8] == report_date.replace("-", ""), "report run/date mismatch")

    candidate_sha = str(payload.get("assured_candidate_head_sha", ""))
    approved_commit = str(payload.get("approved_report_commit_sha", ""))
    _require(SHA_RE.fullmatch(candidate_sha) is not None, "invalid assured candidate head sha")
    _require(SHA_RE.fullmatch(approved_commit) is not None, "invalid approved report commit sha")

    assurance = payload.get("independent_assurance")
    _require(isinstance(assurance, dict), "independent_assurance object required")
    _require(assurance.get("verdict") == "PASS", "independent assurance verdict must be PASS")
    _require(assurance.get("reviewer_role") == "governance_release_assurance", "independent reviewer role mismatch")
    _require(assurance.get("implementation_role_separate") is True, "assurance independence not evidenced")
    _require(str(assurance.get("reviewed_head_sha", "")) == candidate_sha, "assurance head/candidate mismatch")
    _require(bool(str(assurance.get("evidence_ref", "")).strip()), "independent assurance evidence_ref required")

    principal = payload.get("principal_guarded_send_authorization")
    _require(isinstance(principal, dict), "principal guarded-send authorization required")
    _require(principal.get("approved") is True, "principal guarded-send authorization is not approved")
    _require(bool(str(principal.get("reference", "")).strip()), "principal authorization reference required")

    artifacts = payload.get("artifacts")
    _require(isinstance(artifacts, dict), "artifacts object required")
    _require(set(REQUIRED_ARTIFACT_KEYS) <= set(artifacts), "six approved client artifacts required")

    expected_endings = {
        "nl_md": f"weekly_etf_eu_review_nl_{report_suffix}.md",
        "en_md": f"weekly_etf_eu_review_{report_suffix}.md",
        "nl_html": f"weekly_etf_eu_review_nl_{report_suffix}.html",
        "en_html": f"weekly_etf_eu_review_{report_suffix}.html",
        "nl_pdf": f"weekly_etf_eu_review_nl_{report_suffix}.pdf",
        "en_pdf": f"weekly_etf_eu_review_{report_suffix}.pdf",
    }
    for key in REQUIRED_ARTIFACT_KEYS:
        item = artifacts[key]
        _require(isinstance(item, dict), f"artifact {key} must be an object")
        artifact_path = Path(str(item.get("path", "")))
        expected_hash = str(item.get("sha256", "")).lower()
        _require(str(artifact_path).startswith("output/"), f"artifact {key} must be under output/")
        _require(artifact_path.name == expected_endings[key], f"artifact {key} filename/report mismatch")
        _require(artifact_path.exists(), f"approved artifact missing: {artifact_path}")
        _require(SHA256_RE.fullmatch(expected_hash) is not None, f"invalid sha256 for artifact {key}")
        actual_hash = _sha256(artifact_path)
        _require(actual_hash == _normalise_hash(expected_hash), f"artifact hash mismatch: {artifact_path}")

    return payload


def write_delivery_package_manifest(payload: dict[str, Any], output: Path, transport_run_id: str) -> None:
    artifacts = payload["artifacts"]
    manifest = {
        "schema_version": "etf_eu_delivery_package_manifest_v1",
        "run_id": transport_run_id,
        "report_suffix": payload["report_suffix"],
        "dutch_primary_pdf": artifacts["nl_pdf"]["path"],
        "english_companion_pdf": artifacts["en_pdf"]["path"],
        "dutch_primary_html": artifacts["nl_html"]["path"],
        "english_companion_html": artifacts["en_html"]["path"],
        "markdown_source_paths": [artifacts["nl_md"]["path"], artifacts["en_md"]["path"]],
        "pdf_output_available": True,
        "html_output_available": True,
        "dutch_primary": True,
        "english_companion": True,
        "client_grade_package_ready": True,
        "source_is_independently_assured": True,
        "assured_candidate_head_sha": payload["assured_candidate_head_sha"],
        "approved_report_commit_sha": payload["approved_report_commit_sha"],
        "independent_assurance_evidence_ref": payload["independent_assurance"]["evidence_ref"],
        "artifact_hashes_verified": True,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", required=True)
    parser.add_argument("--write-package-manifest")
    parser.add_argument("--transport-run-id")
    args = parser.parse_args()
    payload = validate(Path(args.authority))
    if args.write_package_manifest:
        _require(bool(args.transport_run_id), "--transport-run-id required when writing package manifest")
        write_delivery_package_manifest(payload, Path(args.write_package_manifest), args.transport_run_id)
    print(
        "ETF_EU_GUARDED_DELIVERY_AUTHORITY_OK"
        f" | report_run_id={payload['report_run_id']}"
        f" | report_suffix={payload['report_suffix']}"
        f" | candidate={payload['assured_candidate_head_sha']}"
        f" | approved_commit={payload['approved_report_commit_sha']}"
    )


if __name__ == "__main__":
    main()
