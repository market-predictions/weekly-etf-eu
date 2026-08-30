from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
CLIENT_KEYS = ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _normalise_hash(value: str) -> str:
    value = value.lower()
    return value if value.startswith("sha256:") else "sha256:" + value


def validate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "etf_eu_delivery_package_manifest_v1"
    assert data["dutch_primary"] is True
    assert data["english_companion"] is True
    assert data["valuation_grade"] is False
    assert data["funding_authority"] is False
    assert data["portfolio_mutation"] is False
    assert data["source_is_independently_assured"] is True
    assert data["artifact_hashes_verified"] is True

    source_path = Path(data["source_thin_kernel_manifest_path"])
    source_hash = str(data["source_thin_kernel_manifest_sha256"]).lower()
    assert str(source_path).startswith("output/")
    assert SHA256_RE.fullmatch(source_hash) is not None
    assert source_path.exists(), f"missing source thin-kernel manifest {source_path}"
    assert _sha256(source_path) == _normalise_hash(source_hash), "source thin-kernel manifest hash mismatch"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    assert source["schema_version"] == "etf_eu_thin_kernel_manifest_v1"
    assert source["run_id"] == data["report_run_id"]
    assert source["report_date"] == data["report_date"]
    assert source["report_suffix"] == data["report_suffix"]
    assert source["semantic_state_frozen"] is True
    assert source["post_freeze_semantic_mutation"] is False

    authority = source["authority"]
    for key in ("portfolio_mutation", "trade_ledger_write", "real_broker_execution", "delivery_authority", "smtp_send", "funding_authority"):
        assert authority[key] is False, f"source candidate authority escalated: {key}"

    artifacts = source["artifacts"]
    expected_paths = {
        "nl_md": data["markdown_source_paths"][0],
        "en_md": data["markdown_source_paths"][1],
        "nl_html": data["dutch_primary_html"],
        "en_html": data["english_companion_html"],
        "nl_pdf": data["dutch_primary_pdf"],
        "en_pdf": data["english_companion_pdf"],
    }
    assert len(data["markdown_source_paths"]) == 2
    for key in CLIENT_KEYS:
        item = artifacts[key]
        assert item["path"] == expected_paths[key], f"package/source path mismatch: {key}"
        artifact_path = Path(item["path"])
        assert artifact_path.exists(), f"missing package asset {artifact_path}"
        assert _sha256(artifact_path) == _normalise_hash(str(item["sha256"])), f"package asset hash mismatch: {artifact_path}"

    assert data["pdf_output_available"] is True
    assert data["html_output_available"] is True
    if data["client_grade_package_ready"] is True:
        assert data["stale_delivery_wording_present"] is False
        assert data["main_surface_us_proxy_exposure"] is False
        assert data["main_surface_tbd_candidate_exposure"] is False
        assert data["nan_price_in_client_surface"] is False
    safety_ref = Path(data["client_surface_safety_evidence_ref"])
    assert str(safety_ref).startswith("output/")
    assert safety_ref.exists(), f"missing client-surface safety evidence {safety_ref}"
    return {
        "status": "valid",
        "manifest": str(path),
        "source_thin_kernel_manifest": str(source_path),
        "pdf_output_available": data["pdf_output_available"],
        "html_output_available": data["html_output_available"],
        "client_grade_package_ready": data["client_grade_package_ready"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.manifest)), indent=2))


if __name__ == "__main__":
    main()
