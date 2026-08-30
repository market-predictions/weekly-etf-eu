from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


MATERIAL_FACT_KEYS = (
    "nav_eur",
    "cash_eur",
    "portfolio_period_return_pct",
    "comparator_period_return_pct",
    "active_return_pp",
)
FORBIDDEN_CURRENT_BUILDER_IMPORTS = (
    "finalize_etf_eu_client_surface_semantics",
    "finalize_etf_eu_markdown_semantics",
    "reconcile_etf_eu_funded_markdown",
    "polish_etf_eu_client_grade_html",
    "build_etf_eu_routine_report_package_v2",
)


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def validate(args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[str] = []
    state_path = Path(args.review_state)
    manifest_path = Path(args.manifest)
    state = _load(state_path)
    manifest = _load(manifest_path)

    if state.get("schema_version") != "etf_eu_review_state_v1":
        blockers.append("wrong_review_state_schema")
    if state.get("semantic_state_frozen") is not True:
        blockers.append("review_state_not_frozen")
    if state.get("semantic_mutation_allowed_downstream") is not False:
        blockers.append("downstream_semantic_mutation_not_disabled")
    if state.get("state_valid") is not True:
        blockers.append("review_state_invalid")
    if (state.get("authority") or {}).get("portfolio_mutation") is not False:
        blockers.append("portfolio_mutation_authority_leak")
    if (state.get("authority") or {}).get("delivery_authority") is not False:
        blockers.append("delivery_authority_leak")

    portfolio = state.get("portfolio") or {}
    account = state.get("accountability") or {}
    if account.get("status") != "COMPLETE":
        blockers.append("accountability_incomplete")
    if round(float(portfolio.get("nav_eur") or 0), 2) != round(float(account.get("portfolio_nav_eur") or 0), 2):
        blockers.append("nav_accountability_mismatch")
    decisions = state.get("funded_position_decisions") or []
    if len(decisions) != int(portfolio.get("position_count") or 0):
        blockers.append("funded_position_count_mismatch")
    for row in decisions:
        if row.get("action") not in {"ADD", "HOLD", "REDUCE", "REPLACE", "CLOSE", "REVIEW"}:
            blockers.append(f"invalid_action:{row.get('ticker')}")
        if row.get("unresolved"):
            blockers.append(f"position_unresolved:{row.get('ticker')}")

    artifacts = manifest.get("artifacts") or {}
    for key in ("nl_md", "en_md", "nl_html", "en_html", "nl_pdf", "en_pdf", "review_state"):
        meta = artifacts.get(key) or {}
        path = Path(str(meta.get("path") or ""))
        if not path.exists():
            blockers.append(f"missing_artifact:{key}")
            continue
        if meta.get("sha256") != _sha256(path):
            blockers.append(f"artifact_hash_mismatch:{key}")

    if manifest.get("semantic_state_frozen") is not True or manifest.get("post_freeze_semantic_mutation") is not False:
        blockers.append("manifest_freeze_contract_invalid")
    if manifest.get("semantic_source") != str(state_path):
        blockers.append("manifest_semantic_source_mismatch")

    # Numeric parity: all client text surfaces must contain the same formatted facts.
    nl_md = Path(args.nl_md).read_text(encoding="utf-8")
    en_md = Path(args.en_md).read_text(encoding="utf-8")
    nl_html = Path(args.nl_html).read_text(encoding="utf-8")
    en_html = Path(args.en_html).read_text(encoding="utf-8")
    expected_tokens = [
        f"€{float(portfolio.get('nav_eur')):,.2f}",
        f"€{float(portfolio.get('cash_eur')):,.2f}",
        f"{float(account.get('portfolio_period_return_pct')):.2f}%",
        f"{float(account.get('comparator_period_return_pct')):.2f}%",
    ]
    for token in expected_tokens:
        for surface_name, content in (("nl_md", nl_md), ("en_md", en_md), ("nl_html", nl_html), ("en_html", en_html)):
            if token not in content:
                blockers.append(f"material_fact_missing:{surface_name}:{token}")

    current_builder = Path(args.current_builder).read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_CURRENT_BUILDER_IMPORTS:
        if re.search(rf"\b{re.escape(forbidden)}\b", current_builder):
            blockers.append(f"semantic_patch_dependency_in_current_builder:{forbidden}")

    result = {
        "schema_version": "etf_eu_thin_kernel_validation_v1",
        "valid": not blockers,
        "blockers": blockers,
        "review_state_sha256": _sha256(state_path),
        "semantic_patch_dependency_count": sum(1 for b in blockers if b.startswith("semantic_patch_dependency")),
        "client_surface_count": 6,
    }
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-only validation for Weekly ETF EU Thin Current Kernel")
    parser.add_argument("--review-state", default="output/current/review_state.json")
    parser.add_argument("--manifest", default="output/current/manifest.json")
    parser.add_argument("--nl-md", default="output/current/report_nl.md")
    parser.add_argument("--en-md", default="output/current/report_en.md")
    parser.add_argument("--nl-html", default="output/current/report_nl.html")
    parser.add_argument("--en-html", default="output/current/report_en.html")
    parser.add_argument("--current-builder", default="tools/build_etf_eu_thin_kernel_package.py")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = validate(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["valid"]:
        raise SystemExit("ETF_EU_THIN_KERNEL_VALIDATION_FAILED | " + "; ".join(result["blockers"]))
    print("ETF_EU_THIN_KERNEL_VALIDATION_PASS")


if __name__ == "__main__":
    main()
