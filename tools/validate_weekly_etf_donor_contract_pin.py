from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_RELEASE_ID = "weekly_etf_shared_contract_v1_0_0"
EXPECTED_VERSION = "1.0.0"
EXPECTED_REPOSITORY = "market-predictions/weekly-etf"
EXPECTED_COMMIT = "455201b4736dda41df07644d78b6797282a29fc7"
FORBIDDEN_MUTABLE_REFS = (
    "sync/shared-strategy-state",
    "refs/heads/",
)


def load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Donor contract pin must be a JSON object")
    return payload


def validate(payload: dict[str, Any], repository_root: Path) -> list[str]:
    blockers: list[str] = []
    if payload.get("schema_version") != "etf_eu_donor_contract_pin_v1":
        blockers.append("unexpected pin schema_version")
    if payload.get("contract_release_id") != EXPECTED_RELEASE_ID:
        blockers.append("unexpected contract_release_id")
    if payload.get("semantic_version") != EXPECTED_VERSION:
        blockers.append("unexpected semantic_version")
    if payload.get("donor_repository") != EXPECTED_REPOSITORY:
        blockers.append("unexpected donor_repository")
    commit = str(payload.get("donor_commit_sha") or "")
    if commit != EXPECTED_COMMIT or not re.fullmatch(r"[0-9a-f]{40}", commit):
        blockers.append("donor_commit_sha is not the accepted immutable release commit")
    if payload.get("mutable_donor_branch_allowed") is not False:
        blockers.append("mutable donor branches must be prohibited")
    if payload.get("required_strategy_schema") != "etf_shared_strategy_state_v1":
        blockers.append("strategy schema pin mismatch")
    if payload.get("required_portfolio_schema") != "etf_shared_portfolio_target_v1":
        blockers.append("portfolio schema pin mismatch")

    authority = payload.get("authority") if isinstance(payload.get("authority"), dict) else {}
    for key in (
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "production_delivery_authority",
    ):
        if authority.get(key) is not False:
            blockers.append(f"{key} must be false")

    rollback = payload.get("rollback") if isinstance(payload.get("rollback"), dict) else {}
    if rollback.get("last_accepted_donor_commit_sha") != EXPECTED_COMMIT:
        blockers.append("rollback donor commit must match the accepted v1.0.0 release")
    if rollback.get("automatic_portfolio_mutation") is not False:
        blockers.append("rollback must not mutate the portfolio automatically")
    if rollback.get("automatic_trade_reversal") is not False:
        blockers.append("rollback must not reverse trades automatically")

    workflow_paths = payload.get("workflow_paths") if isinstance(payload.get("workflow_paths"), list) else []
    if len(workflow_paths) != 4:
        blockers.append("exactly four donor-consuming workflows must be registered")
    for raw_path in workflow_paths:
        path = repository_root / str(raw_path)
        if not path.is_file():
            blockers.append(f"registered workflow is missing: {raw_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if f"repository: {EXPECTED_REPOSITORY}" not in text:
            blockers.append(f"workflow does not checkout the expected donor repository: {raw_path}")
        if f"ref: {EXPECTED_COMMIT}" not in text:
            blockers.append(f"workflow is not pinned to the accepted donor commit: {raw_path}")
        for forbidden in FORBIDDEN_MUTABLE_REFS:
            if forbidden in text:
                blockers.append(f"workflow contains forbidden mutable donor ref {forbidden!r}: {raw_path}")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the immutable Weekly ETF donor contract pin")
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("config/weekly_etf_donor_contract_pin.json"),
    )
    args = parser.parse_args()
    payload = load(args.path)
    repository_root = Path(__file__).resolve().parents[1]
    blockers = validate(payload, repository_root)
    print(json.dumps({
        "artifact_type": "etf_eu_donor_contract_pin_validation",
        "contract_release_id": payload.get("contract_release_id"),
        "donor_commit_sha": payload.get("donor_commit_sha"),
        "valid": not blockers,
        "blockers": blockers,
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
