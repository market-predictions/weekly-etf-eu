from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_OUTPUT_DIR = Path("output/pricing")
ALLOWED_SOURCE_IDS = {"euronext_live", "deutsche_boerse_live"}
ALLOWED_EVIDENCE_STATUSES = {"official_page_reachable", "official_page_unresolved"}
ALLOWED_OBSERVATION_STATUSES = {"candidate_text_observed", "no_candidate_text_observed"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_file(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("ucits_official_exchange_page_evidence_*.json"))
    if not files:
        raise RuntimeError(f"No official exchange page evidence artifacts found in {output_dir}")
    return files[-1]


def text(value: Any) -> str:
    return str(value or "").strip()


def validate(path: Path) -> None:
    payload = load_json(path)
    errors: list[str] = []
    if payload.get("schema_version") != "ucits_official_exchange_page_evidence_v1":
        errors.append("schema_version_must_be_ucits_official_exchange_page_evidence_v1")
    for field in ["portfolio_mutation", "production_delivery", "funding_authority", "valuation_authority"]:
        if payload.get(field) is not False:
            errors.append(f"top_level_{field}_must_be_false")

    rows = payload.get("rows") or []
    if not isinstance(rows, list) or not rows:
        errors.append("at_least_one_official_exchange_page_evidence_row_required")
    candidate_observed = 0
    for idx, row in enumerate(rows):
        label = f"row:{idx}:{row.get('registry_id') or 'unknown'}"
        for field in [
            "registry_id",
            "isin",
            "exchange",
            "exchange_ticker",
            "trading_currency",
            "provider_symbol",
            "source_id",
            "authority",
            "product_url",
            "expected_currency",
            "evidence_status",
            "candidate_observation_status",
        ]:
            if not text(row.get(field)):
                errors.append(f"{label}:missing_{field}")
        if row.get("source_id") not in ALLOWED_SOURCE_IDS:
            errors.append(f"{label}:unexpected_source_id:{row.get('source_id')}")
        if row.get("evidence_status") not in ALLOWED_EVIDENCE_STATUSES:
            errors.append(f"{label}:unexpected_evidence_status:{row.get('evidence_status')}")
        if row.get("candidate_observation_status") not in ALLOWED_OBSERVATION_STATUSES:
            errors.append(f"{label}:unexpected_candidate_observation_status:{row.get('candidate_observation_status')}")
        if not isinstance(row.get("expected_token_checks"), list):
            errors.append(f"{label}:expected_token_checks_must_be_list")
        if not isinstance(row.get("candidate_price_date_currency_text"), list):
            errors.append(f"{label}:candidate_price_date_currency_text_must_be_list")
        if row.get("candidate_observation_status") == "candidate_text_observed":
            candidate_observed += 1
            if not row.get("candidate_price_date_currency_text"):
                errors.append(f"{label}:candidate_text_observed_requires_candidate_text")
        if row.get("price_extraction") is not False:
            errors.append(f"{label}:price_extraction_must_be_false")
        for field in ["portfolio_mutation", "production_delivery", "funding_authority", "valuation_authority"]:
            if row.get(field) is not False:
                errors.append(f"{label}:{field}_must_be_false")
    if errors:
        raise RuntimeError("Official exchange page evidence validation failed: " + "; ".join(errors))
    reachable = sum(1 for row in rows if row.get("evidence_status") == "official_page_reachable")
    print(f"UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_VALIDATION_OK | artifact={path} | rows={len(rows)} | reachable={reachable} | candidate_observed={candidate_observed}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default=None)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    artifact = Path(args.artifact) if args.artifact else latest_file(Path(args.output_dir))
    validate(artifact)


if __name__ == "__main__":
    main()
