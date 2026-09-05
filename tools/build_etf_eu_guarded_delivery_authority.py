#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "etf_eu_guarded_delivery_authority_v1"
ARTIFACT_TYPE = "etf_eu_guarded_delivery_authority"
PRODUCT = "weekly_etf_eu"
SAFETY_SCHEMA = "etf_eu_client_surface_safety_v1"
REQUIRED_ARTIFACT_KEYS = ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required evidence missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"required evidence must be JSON object: {path}")
    return payload


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def build_authority(
    *,
    thin_kernel_manifest_path: Path,
    safety_evidence_path: Path,
    assured_candidate_head_sha: str,
    approved_report_commit_sha: str,
    assurance_evidence_ref: str,
    principal_authorization_ref: str,
    confirm_independent_assurance_pass: bool,
    confirm_role_separation: bool,
    confirm_principal_guarded_send_authorization: bool,
    output: Path,
) -> dict[str, Any]:
    _require(SHA_RE.fullmatch(assured_candidate_head_sha) is not None, "invalid assured candidate head sha")
    _require(SHA_RE.fullmatch(approved_report_commit_sha) is not None, "invalid approved report commit sha")
    _require(confirm_independent_assurance_pass, "independent assurance PASS must be explicitly confirmed")
    _require(confirm_role_separation, "implementation/assurance role separation must be explicitly confirmed")
    _require(confirm_principal_guarded_send_authorization, "principal guarded-send authorization must be explicitly confirmed")
    _require(bool(assurance_evidence_ref.strip()), "assurance evidence reference required")
    _require(bool(principal_authorization_ref.strip()), "principal authorization reference required")

    manifest = _load(thin_kernel_manifest_path)
    _require(manifest.get("schema_version") == "etf_eu_thin_kernel_manifest_v1", "thin kernel manifest schema mismatch")
    _require(manifest.get("semantic_state_frozen") is True, "thin kernel semantic state is not frozen")
    _require(manifest.get("post_freeze_semantic_mutation") is False, "thin kernel post-freeze mutation contract invalid")
    candidate_authority = manifest.get("authority") or {}
    for key in ("portfolio_mutation", "trade_ledger_write", "real_broker_execution", "delivery_authority", "smtp_send", "funding_authority"):
        _require(candidate_authority.get(key) is False, f"candidate authority escalated before delivery: {key}")

    safety = _load(safety_evidence_path)
    _require(safety.get("schema_version") == SAFETY_SCHEMA, "client surface safety schema mismatch")
    _require(safety.get("valid") is True and safety.get("status") == "PASS", "client surface safety evidence must PASS")
    safety_flags = safety.get("client_surface_safety") or {}
    for key in (
        "stale_delivery_wording_present",
        "main_surface_us_proxy_exposure",
        "main_surface_tbd_candidate_exposure",
        "nan_price_in_client_surface",
    ):
        _require(safety_flags.get(key) is False, f"client surface safety assertion failed: {key}")
    bound_manifest = safety.get("thin_kernel_manifest") or {}
    _require(str(bound_manifest.get("path") or "") == str(thin_kernel_manifest_path), "safety evidence bound to different thin kernel manifest")
    _require(str(bound_manifest.get("sha256") or "").lower() == _sha256(thin_kernel_manifest_path), "safety evidence thin kernel manifest hash mismatch")

    report_date = str(manifest.get("report_date") or "")
    report_suffix = str(manifest.get("report_suffix") or "")
    report_run_id = str(manifest.get("run_id") or "")
    _require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_date) is not None, "invalid report_date in thin kernel manifest")
    _require(re.fullmatch(r"\d{6}", report_suffix) is not None, "invalid report_suffix in thin kernel manifest")
    _require(re.fullmatch(r"\d{8}_\d{6}", report_run_id) is not None, "invalid run_id in thin kernel manifest")

    manifest_artifacts = manifest.get("artifacts") or {}
    artifacts: dict[str, dict[str, str]] = {}
    for key in REQUIRED_ARTIFACT_KEYS:
        item = manifest_artifacts.get(key)
        _require(isinstance(item, dict), f"thin kernel manifest artifact missing: {key}")
        path = Path(str(item.get("path") or ""))
        _require(path.exists(), f"thin kernel artifact missing: {path}")
        declared = str(item.get("sha256") or "").removeprefix("sha256:").lower()
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        _require(declared == actual, f"thin kernel artifact hash mismatch: {key}")
        artifacts[key] = {"path": str(path), "sha256": "sha256:" + actual}

    payload = {
        "schema_version": SCHEMA,
        "artifact_type": ARTIFACT_TYPE,
        "product": PRODUCT,
        "generated_at_utc": _utc_now(),
        "status": "APPROVED_FOR_GUARDED_DELIVERY",
        "delivery_authority": True,
        "portfolio_mutation": False,
        "broker_execution": False,
        "report_date": report_date,
        "report_suffix": report_suffix,
        "report_run_id": report_run_id,
        "assured_candidate_head_sha": assured_candidate_head_sha,
        "approved_report_commit_sha": approved_report_commit_sha,
        "thin_kernel_manifest": {
            "path": str(thin_kernel_manifest_path),
            "sha256": _sha256(thin_kernel_manifest_path),
        },
        "independent_assurance": {
            "verdict": "PASS",
            "reviewer_role": "governance_release_assurance",
            "implementation_role_separate": True,
            "reviewed_head_sha": assured_candidate_head_sha,
            "evidence_ref": assurance_evidence_ref,
        },
        "principal_guarded_send_authorization": {
            "approved": True,
            "reference": principal_authorization_ref,
        },
        "client_surface_safety": {
            **safety_flags,
            "evidence_ref": str(safety_evidence_path),
            "evidence_sha256": _sha256(safety_evidence_path),
        },
        "artifacts": artifacts,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build exact-manifest ETF EU guarded-delivery authority without executing transport")
    parser.add_argument("--thin-kernel-manifest", default="output/current/manifest.json")
    parser.add_argument("--client-surface-safety-evidence", required=True)
    parser.add_argument("--assured-candidate-head-sha", required=True)
    parser.add_argument("--approved-report-commit-sha", required=True)
    parser.add_argument("--assurance-evidence-ref", required=True)
    parser.add_argument("--principal-authorization-ref", required=True)
    parser.add_argument("--confirm-independent-assurance-pass", action="store_true")
    parser.add_argument("--confirm-role-separation", action="store_true")
    parser.add_argument("--confirm-principal-guarded-send-authorization", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = build_authority(
        thin_kernel_manifest_path=Path(args.thin_kernel_manifest),
        safety_evidence_path=Path(args.client_surface_safety_evidence),
        assured_candidate_head_sha=args.assured_candidate_head_sha,
        approved_report_commit_sha=args.approved_report_commit_sha,
        assurance_evidence_ref=args.assurance_evidence_ref,
        principal_authorization_ref=args.principal_authorization_ref,
        confirm_independent_assurance_pass=args.confirm_independent_assurance_pass,
        confirm_role_separation=args.confirm_role_separation,
        confirm_principal_guarded_send_authorization=args.confirm_principal_guarded_send_authorization,
        output=Path(args.output),
    )
    print(
        "ETF_EU_GUARDED_DELIVERY_AUTHORITY_BUILT"
        f" | report_run_id={payload['report_run_id']}"
        f" | candidate={payload['assured_candidate_head_sha']}"
        f" | approved_commit={payload['approved_report_commit_sha']}"
        " | transport_executed=false"
    )


if __name__ == "__main__":
    main()
