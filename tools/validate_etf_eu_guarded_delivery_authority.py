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
THIN_KERNEL_SCHEMA = "etf_eu_thin_kernel_manifest_v1"
REQUIRED_ARTIFACT_KEYS = ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")
REQUIRED_CLIENT_SURFACE_FALSE_FLAGS = (
    "stale_delivery_wording_present",
    "main_surface_us_proxy_exposure",
    "main_surface_tbd_candidate_exposure",
    "nan_price_in_client_surface",
)
REQUIRED_THIN_KERNEL_FALSE_AUTHORITY = (
    "portfolio_mutation",
    "trade_ledger_write",
    "real_broker_execution",
    "delivery_authority",
    "smtp_send",
    "funding_authority",
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _normalise_hash(value: str) -> str:
    value = value.lower()
    return value if value.startswith("sha256:") else "sha256:" + value


def _load(path: Path) -> dict[str, Any]:
    _require(path.exists(), f"JSON evidence missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(payload, dict), f"JSON evidence must be an object: {path}")
    return payload


def _validate_bound_thin_kernel_manifest(
    payload: dict[str, Any], *, report_date: str, report_suffix: str, report_run_id: str
) -> tuple[Path, str, dict[str, Any]]:
    binding = payload.get("thin_kernel_manifest")
    _require(isinstance(binding, dict), "thin_kernel_manifest binding required")
    manifest_path = Path(str(binding.get("path", "")))
    declared_hash = str(binding.get("sha256", "")).lower()
    _require(str(manifest_path).startswith("output/"), "thin kernel manifest must be under output/")
    _require(SHA256_RE.fullmatch(declared_hash) is not None, "invalid thin kernel manifest sha256")
    actual_hash = _sha256(manifest_path)
    _require(actual_hash == _normalise_hash(declared_hash), "thin kernel manifest hash mismatch")

    manifest = _load(manifest_path)
    _require(manifest.get("schema_version") == THIN_KERNEL_SCHEMA, "thin kernel manifest schema mismatch")
    _require(str(manifest.get("run_id", "")) == report_run_id, "thin kernel manifest run mismatch")
    _require(str(manifest.get("report_date", "")) == report_date, "thin kernel manifest report_date mismatch")
    _require(str(manifest.get("report_suffix", "")) == report_suffix, "thin kernel manifest report_suffix mismatch")
    _require(manifest.get("semantic_state_frozen") is True, "thin kernel semantic state is not frozen")
    _require(manifest.get("post_freeze_semantic_mutation") is False, "thin kernel allows post-freeze semantic mutation")

    authority = manifest.get("authority")
    _require(isinstance(authority, dict), "thin kernel authority object required")
    for key in REQUIRED_THIN_KERNEL_FALSE_AUTHORITY:
        _require(authority.get(key) is False, f"thin kernel candidate authority escalated: {key}")

    manifest_artifacts = manifest.get("artifacts")
    _require(isinstance(manifest_artifacts, dict), "thin kernel artifacts object required")
    _require(set(REQUIRED_ARTIFACT_KEYS) <= set(manifest_artifacts), "thin kernel manifest lacks six client artifacts")
    review_state = manifest_artifacts.get("review_state")
    _require(isinstance(review_state, dict), "thin kernel review_state artifact required")
    semantic_source = str(manifest.get("semantic_source", ""))
    _require(semantic_source == str(review_state.get("path", "")), "thin kernel semantic_source/review_state mismatch")
    review_state_path = Path(semantic_source)
    _require(str(review_state_path).startswith("output/"), "review_state must be under output/")
    review_state_hash = str(review_state.get("sha256", "")).lower()
    _require(SHA256_RE.fullmatch(review_state_hash) is not None, "invalid review_state sha256")
    _require(_sha256(review_state_path) == _normalise_hash(review_state_hash), "review_state hash mismatch")
    return manifest_path, actual_hash, manifest


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

    safety = payload.get("client_surface_safety")
    _require(isinstance(safety, dict), "client_surface_safety object required")
    for flag in REQUIRED_CLIENT_SURFACE_FALSE_FLAGS:
        _require(safety.get(flag) is False, f"client surface safety assertion failed: {flag}")
    safety_evidence = Path(str(safety.get("evidence_ref", "")))
    _require(str(safety_evidence).startswith("output/"), "client surface safety evidence must be under output/")
    _require(safety_evidence.exists(), f"client surface safety evidence missing: {safety_evidence}")

    manifest_path, manifest_hash, thin_manifest = _validate_bound_thin_kernel_manifest(
        payload, report_date=report_date, report_suffix=report_suffix, report_run_id=report_run_id
    )
    manifest_artifacts = thin_manifest["artifacts"]
    artifacts = payload.get("artifacts")
    _require(isinstance(artifacts, dict), "artifacts object required")
    _require(set(REQUIRED_ARTIFACT_KEYS) <= set(artifacts), "six approved client artifacts required")
    for key in REQUIRED_ARTIFACT_KEYS:
        item = artifacts[key]
        source = manifest_artifacts[key]
        _require(isinstance(item, dict), f"artifact {key} must be an object")
        _require(isinstance(source, dict), f"thin kernel artifact {key} must be an object")
        artifact_path = Path(str(item.get("path", "")))
        expected_hash = str(item.get("sha256", "")).lower()
        source_path = str(source.get("path", ""))
        source_hash = str(source.get("sha256", "")).lower()
        _require(str(artifact_path).startswith("output/"), f"artifact {key} must be under output/")
        _require(artifact_path.exists(), f"approved artifact missing: {artifact_path}")
        _require(SHA256_RE.fullmatch(expected_hash) is not None, f"invalid sha256 for artifact {key}")
        _require(str(artifact_path) == source_path, f"artifact {key} path differs from thin kernel manifest")
        _require(_normalise_hash(expected_hash) == _normalise_hash(source_hash), f"artifact {key} hash differs from thin kernel manifest")
        _require(_sha256(artifact_path) == _normalise_hash(expected_hash), f"artifact hash mismatch: {artifact_path}")

    payload["_validated_thin_kernel_manifest"] = {"path": str(manifest_path), "sha256": manifest_hash}
    return payload


def write_delivery_package_manifest(payload: dict[str, Any], output: Path, transport_run_id: str) -> None:
    artifacts = payload["artifacts"]
    safety = payload["client_surface_safety"]
    source_manifest = payload.get("_validated_thin_kernel_manifest") or payload["thin_kernel_manifest"]
    manifest = {
        "schema_version": "etf_eu_delivery_package_manifest_v1",
        "run_id": transport_run_id,
        "report_run_id": payload["report_run_id"],
        "report_date": payload["report_date"],
        "report_suffix": payload["report_suffix"],
        "source_thin_kernel_manifest_path": source_manifest["path"],
        "source_thin_kernel_manifest_sha256": _normalise_hash(str(source_manifest["sha256"])),
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
        "stale_delivery_wording_present": safety["stale_delivery_wording_present"],
        "main_surface_us_proxy_exposure": safety["main_surface_us_proxy_exposure"],
        "main_surface_tbd_candidate_exposure": safety["main_surface_tbd_candidate_exposure"],
        "nan_price_in_client_surface": safety["nan_price_in_client_surface"],
        "client_surface_safety_evidence_ref": safety["evidence_ref"],
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
