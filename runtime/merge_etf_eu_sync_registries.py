from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"Registry file is missing: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def merge(base: dict[str, Any], additions: dict[str, Any]) -> dict[str, Any]:
    base_funds = [row for row in (base.get("funds") or []) if isinstance(row, dict)]
    added_funds = [row for row in (additions.get("funds") or []) if isinstance(row, dict)]
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for row in base_funds + added_funds:
        registry_id = str(row.get("registry_id") or "").strip()
        if not registry_id:
            raise RuntimeError("Every registry fund requires registry_id")
        if registry_id not in order:
            order.append(registry_id)
        by_id[registry_id] = row

    duplicates_in_additions = sorted(
        {
            str(row.get("registry_id"))
            for row in added_funds
            if sum(1 for item in added_funds if item.get("registry_id") == row.get("registry_id")) > 1
        }
    )
    if duplicates_in_additions:
        raise RuntimeError("Duplicate supplemental registry IDs: " + ", ".join(duplicates_in_additions))

    return {
        "schema_version": "ucits_symbol_registry_sync_merged_v1",
        "status": "shadow_only",
        "base_registry_schema_version": base.get("schema_version"),
        "supplemental_registry_schema_version": additions.get("schema_version"),
        "production_registry_overwrite": False,
        "funds": [by_id[registry_id] for registry_id in order],
        "merge_evidence": {
            "base_fund_count": len(base_funds),
            "supplemental_fund_count": len(added_funds),
            "merged_fund_count": len(order),
            "supplemental_override_ids": sorted(
                set(str(row.get("registry_id")) for row in base_funds)
                & set(str(row.get("registry_id")) for row in added_funds)
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge production and shadow UCITS registries without mutating the base registry")
    parser.add_argument("--base", type=Path, default=Path("config/ucits_symbol_registry.yml"))
    parser.add_argument("--additions", type=Path, default=Path("config/ucits_symbol_registry_sync_additions.yml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = merge(load_yaml(args.base), load_yaml(args.additions))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
