from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "euronext_endpoint_evidence_v1"
TARGET_CANDIDATE_NAME = "settings_search_product_data"
DEFAULT_OUTPUT_DIR = Path("output/pricing")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_euronext_rows(close_observations: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row for row in close_observations.get("rows", [])
        if isinstance(row, dict) and row.get("source_id") == "euronext_live"
    ]


def _candidate_evidence(row: dict[str, Any]) -> dict[str, Any]:
    lineage = row.get("source_lineage") if isinstance(row.get("source_lineage"), dict) else {}
    diagnostics = lineage.get("adapter_diagnostics") if isinstance(lineage.get("adapter_diagnostics"), dict) else {}
    product_page = diagnostics.get("product_page_signal_diagnostics") if isinstance(diagnostics.get("product_page_signal_diagnostics"), dict) else {}
    evidence = product_page.get("quote_endpoint_candidate_evidence") if isinstance(product_page.get("quote_endpoint_candidate_evidence"), dict) else {}
    return evidence


def _target_candidate(candidate_evidence: dict[str, Any]) -> dict[str, str] | None:
    for candidate in candidate_evidence.get("candidate_urls") or []:
        if isinstance(candidate, dict) and candidate.get("name") == TARGET_CANDIDATE_NAME and candidate.get("url"):
            return {"name": str(candidate.get("name")), "url": str(candidate.get("url"))}
    return None


def _fetch_sample(url: str) -> dict[str, Any]:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(7000)
            text = raw.decode("utf-8", errors="replace")
            return {
                "http_status": getattr(response, "status", None),
                "final_url": getattr(response, "url", None),
                "content_type": response.headers.get("content-type"),
                "bytes_sampled": len(raw),
                "body_sample": re.sub(r"\s+", " ", text[:900]).strip(),
                "fetch_error": None,
            }
    except Exception as exc:  # pragma: no cover - provider dependent
        return {
            "http_status": None,
            "final_url": url,
            "content_type": None,
            "bytes_sampled": 0,
            "body_sample": "",
            "fetch_error": str(exc),
        }


def _signals(sample: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    text = str(sample.get("body_sample") or "")
    lower = text.lower()
    return {
        "contains_isin": str(row.get("isin") or "").lower() in lower,
        "contains_exchange_ticker": str(row.get("exchange_ticker") or "").lower() in lower,
        "contains_provider_symbol": str(row.get("provider_symbol") or "").lower() in lower,
        "contains_quote_terms": any(term in lower for term in ["quote", "price", "last", "close", "currency"]),
        "looks_json": text.lstrip().startswith(("{", "[")),
    }


def build(close_observations_path: Path, output_dir: Path, run_id: str) -> Path:
    close_observations = _load_json(close_observations_path)
    rows: list[dict[str, Any]] = []
    for row in _walk_euronext_rows(close_observations):
        evidence = _candidate_evidence(row)
        candidate = _target_candidate(evidence)
        if not candidate:
            rows.append({
                "registry_id": row.get("registry_id"),
                "source_id": row.get("source_id"),
                "target_candidate_name": TARGET_CANDIDATE_NAME,
                "evidence_status": "target_candidate_missing",
                "authority": False,
                "candidate_close_extraction": False,
                "completed_session_validation": False,
                "valuation_authority": False,
                "funding_authority": False,
                "portfolio_mutation": False,
                "production_delivery": False,
            })
            continue
        sample = _fetch_sample(candidate["url"])
        rows.append({
            "registry_id": row.get("registry_id"),
            "isin": row.get("isin"),
            "exchange_ticker": row.get("exchange_ticker"),
            "provider_symbol": row.get("provider_symbol"),
            "source_id": row.get("source_id"),
            "target_candidate_name": TARGET_CANDIDATE_NAME,
            "target_url": candidate["url"],
            "evidence_status": "endpoint_sample_observed" if sample.get("fetch_error") is None else "endpoint_fetch_failed",
            "fetch": sample,
            "signals": _signals(sample, row),
            "authority": False,
            "candidate_close_extraction": False,
            "completed_session_validation": False,
            "valuation_authority": False,
            "funding_authority": False,
            "portfolio_mutation": False,
            "production_delivery": False,
        })
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(close_observations_path),
        "target_candidate_name": TARGET_CANDIDATE_NAME,
        "diagnostic_only": True,
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"euronext_endpoint_evidence_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"EURONEXT_ENDPOINT_EVIDENCE_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--close-observations", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.close_observations), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
