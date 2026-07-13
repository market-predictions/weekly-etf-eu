from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load(path: Path) -> dict[str, Any]:
    _require(path.exists(), f"missing artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_result(
    *,
    result_path: Path,
    package_path: Path,
    expected_mode: str,
) -> dict[str, Any]:
    result = _load(result_path)
    package = _load(package_path)
    _require(result.get("schema_version") == "etf_eu_corrected_transport_result_v1", "result schema mismatch")
    _require(result.get("artifact_type") == "etf_eu_corrected_transport_result", "result type mismatch")
    _require(result.get("correction_transport") is True, "correction transport flag missing")
    _require(result.get("correction_control_id") == package.get("correction_control_id"), "control id mismatch")
    _require(result.get("source_run_id") == package.get("source_run_id"), "source run mismatch")
    _require(result.get("repair_run_id") == package.get("repair_run_id"), "repair run mismatch")
    _require(result.get("report_date") == package.get("report_date"), "report date mismatch")
    _require(str(result.get("report_suffix")) == str(package.get("report_suffix")), "report suffix mismatch")
    _require(result.get("delivery_mode") == expected_mode, "delivery mode mismatch")
    _require(result.get("receipt_confirmed") is False, "receipt must remain false")
    _require(result.get("original_transport_evidence_overwritten") is False, "original evidence overwrite flag changed")
    _require(result.get("attachment_count") == 4, "corrected attachment count must be four")
    for key in (
        "recipient_plaintext_values_exposed",
        "secret_values_exposed",
        "raw_email_content_stored",
        "raw_receipt_pdf_stored_in_github",
        "valuation_grade",
        "funding_authority",
        "portfolio_mutation",
        "production_delivery_authority",
    ):
        _require(result.get(key) is False, f"{key} must be false")

    expected_paths = package.get("corrected_delivery_files") or {}
    actual_paths = result.get("attachment_paths") or []
    _require(set(actual_paths) == set(expected_paths.values()), "result attachment paths do not match corrected package")
    hashes = result.get("attachment_sha256") or {}
    for label, path_value in expected_paths.items():
        path = Path(path_value)
        _require(path.exists(), f"corrected attachment missing: {path}")
        _require(_sha256(path) == str(hashes.get(label)), f"result attachment hash mismatch: {label}")
        _require(_sha256(path) == str((package.get("delivery_sha256") or {}).get(label)), f"package attachment hash mismatch: {label}")

    evidence_path = Path(str(result.get("delivery_evidence_path") or ""))
    evidence = _load(evidence_path)
    _require(evidence.get("schema_version") == "etf_eu_corrected_delivery_evidence_v1", "evidence schema mismatch")
    _require(evidence.get("correction_transport") is True, "evidence correction flag missing")
    _require(evidence.get("receipt_confirmed") is False, "evidence receipt must remain false")
    _require(evidence.get("recipient_data_policy") == "redacted_hash_only", "recipient policy mismatch")
    _require(evidence.get("attachment_count") == 4, "evidence attachment count mismatch")
    _require(evidence.get("original_transport_evidence_overwritten") is False, "evidence overwrite flag changed")

    if expected_mode == "dry_run":
        _require(result.get("transport_attempted") is False, "dry-run attempted transport")
        _require(result.get("transport_success") is False, "dry-run claimed transport success")
        _require(result.get("send_executed") is False, "dry-run claimed send execution")
        _require(result.get("delivery_status") == "dry_run_no_transport", "dry-run status mismatch")
    elif expected_mode == "send":
        _require(result.get("transport_attempted") is True, "send did not attempt transport")
        _require(result.get("transport_success") is True, "corrected transport did not succeed")
        _require(result.get("send_executed") is True, "successful transport missing send_executed")
        _require(result.get("delivery_status") == "smtp_sendmail_returned_no_exception", "send status mismatch")
    else:
        raise RuntimeError(f"unsupported expected mode: {expected_mode}")

    return {
        "status": "valid",
        "result": str(result_path),
        "evidence": str(evidence_path),
        "delivery_mode": expected_mode,
        "transport_attempted": result["transport_attempted"],
        "transport_success": result["transport_success"],
        "receipt_confirmed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ETF EU corrected transport result and evidence.")
    parser.add_argument("--result", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--expected-mode", choices=["dry_run", "send"], required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            validate_result(
                result_path=Path(args.result),
                package_path=Path(args.package),
                expected_mode=args.expected_mode,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
