from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Manifest must be a JSON object")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_wp09_cutover_readiness_manifest_v1":
        blockers.append("unexpected manifest schema")
    if payload.get("status") not in {"blocked_not_activation_ready", "evidence_passed_pending_separate_authorization_package"}:
        blockers.append("invalid manifest status")
    evidence_path = Path(str(payload.get("evidence_artifact") or ""))
    decision_path = Path(str(payload.get("decision_artifact") or ""))
    for path, digest_key, label in (
        (evidence_path, "evidence_sha256", "evidence"),
        (decision_path, "decision_sha256", "decision"),
    ):
        if not path.is_file():
            blockers.append(f"missing {label} artifact: {path}")
        elif payload.get(digest_key) != sha256_file(path):
            blockers.append(f"{label} digest mismatch")
    if payload.get("activation_ready") is not False or payload.get("stage_1_activation_authorized") is not False:
        blockers.append("manifest must remain non-authorizing")
    if payload.get("executable_trade_intents") not in ([], None):
        blockers.append("manifest contains executable trade intents")
    for key in ("portfolio_mutation", "ledger_write", "funding_authority", "execution_authority", "production_delivery_authority"):
        if payload.get(key) is not False:
            blockers.append(f"manifest {key} must be false")
    protected = payload.get("protected_state") if isinstance(payload.get("protected_state"), dict) else {}
    if not protected.get("portfolio_sha256") or not protected.get("ledger_sha256"):
        blockers.append("protected-state hashes missing")
    if payload.get("status") == "blocked_not_activation_ready" and int(payload.get("blocker_count") or 0) <= 0:
        blockers.append("blocked manifest has no blockers")
    return blockers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    payload = load(args.path)
    blockers = validate(payload)
    print(json.dumps({
        "artifact_type": "etf_eu_wp09_cutover_readiness_manifest_validation",
        "valid": not blockers,
        "status": payload.get("status"),
        "blockers": blockers,
        "manifest_blocker_count": int(payload.get("blocker_count") or 0),
    }, indent=2, ensure_ascii=False))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
