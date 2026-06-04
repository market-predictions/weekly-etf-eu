from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pricing.valuation_agreement_evidence import build_agreement_gate_evidence


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def enrich_valuation_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for row in payload.get("rows") or []:
        updated = dict(row)
        gate = build_agreement_gate_evidence(
            row,
            non_authoritative_preflight_evidence=row.get("non_authoritative_preflight_evidence"),
            twelve_data_candidate_evidence=row.get("twelve_data_candidate_evidence"),
        )
        blockers = list(updated.get("valuation_blockers") or [])
        if gate.get("status") == "valuation_grade":
            blockers.append("agreement_gate_evidence_not_promoted_by_valuation_artifact_policy")
        else:
            blockers.append("agreement_gate_no_valuation_grade_agreement")
        updated["agreement_gate_evidence"] = gate
        updated["valuation_blockers"] = blockers
        updated["valuation_grade"] = False
        updated["pricing_source"] = None
        updated["source_authority"] = None
        updated["observed_date"] = None
        updated["close"] = None
        updated["currency"] = None
        updated["completed_session"] = False
        updated["portfolio_mutation"] = False
        updated["production_delivery"] = False
        updated["funding_authority"] = False
        rows.append(updated)

    enriched = dict(payload)
    enriched["rows"] = rows
    enriched["agreement_gate_enriched_at_utc"] = datetime.now(timezone.utc).isoformat()
    enriched["agreement_gate_row_count"] = len(rows)
    enriched["agreement_gate_valuation_grade_evidence_count"] = sum(
        1 for row in rows if (row.get("agreement_gate_evidence") or {}).get("status") == "valuation_grade"
    )
    enriched["valuation_grade_row_count"] = 0
    enriched["portfolio_mutation"] = False
    enriched["production_delivery"] = False
    enriched["funding_authority"] = False
    return enriched


def write_enriched_artifact(input_path: Path, output_path: Path) -> Path:
    enriched = enrich_valuation_artifact(_load(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(enriched, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "UCITS_VALUATION_AGREEMENT_ENRICHMENT_OK"
        f" | input={input_path}"
        f" | output={output_path}"
        f" | rows={enriched['agreement_gate_row_count']}"
        f" | agreement_gate_valuation_grade_evidence={enriched['agreement_gate_valuation_grade_evidence_count']}"
        " | valuation_grade_rows=0 | portfolio_mutation=false | delivery=false"
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_enriched_artifact(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
