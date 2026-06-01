from __future__ import annotations

import argparse
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "issuer_reference_sanity_gate_v1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def fetch_text(url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,*/*;q=0.8"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(90000)
            text = raw.decode("utf-8", errors="replace")
            return {
                "http_status": getattr(response, "status", None),
                "final_url": getattr(response, "url", url),
                "content_type": response.headers.get("content-type"),
                "bytes_sampled": len(raw),
                "text": text,
                "fetch_error": None,
            }
    except Exception as exc:
        return {"http_status": None, "final_url": url, "content_type": None, "bytes_sampled": 0, "text": "", "fetch_error": str(exc)}


def policy_by_registry(policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row.get("registry_id")): row for row in policy.get("issuer_products", []) or [] if isinstance(row, dict)}


def row_key(row: dict[str, Any]) -> str:
    return str(row.get("registry_id") or "")


def compact_sample(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text[:900])).strip()


def evaluate_row(yahoo_row: dict[str, Any], cross_source_row: dict[str, Any] | None, issuer_policy: dict[str, Any], policy_rules: dict[str, Any]) -> dict[str, Any]:
    registry_id = row_key(yahoo_row)
    issuer = issuer_policy.get(registry_id)
    fetch = fetch_text(str(issuer.get("product_url"))) if issuer and issuer.get("product_url") else {"http_status": None, "final_url": None, "content_type": None, "bytes_sampled": 0, "text": "", "fetch_error": "issuer_product_url_missing"}
    text = str(fetch.get("text") or "")
    lower = text.lower()
    expected_tokens = issuer.get("expected_tokens") if isinstance(issuer, dict) else []
    token_matches = {str(token): (str(token).lower() in lower) for token in expected_tokens or []}
    isin = str(yahoo_row.get("isin") or "")
    identity_match = bool(isin and isin.lower() in lower and token_matches and all(token_matches.values()))
    reference_price_found = False
    broad_tolerance_passed = False
    gates = {
        "issuer_policy_present": issuer is not None,
        "issuer_page_fetch_ok": fetch.get("http_status") == 200,
        "issuer_identity_match": identity_match,
        "reference_price_found": reference_price_found,
        "broad_tolerance_check_passed": broad_tolerance_passed,
        "cross_source_gate_already_passed": bool(cross_source_row and cross_source_row.get("cross_source_check_passed") is True),
    }
    failed = [key for key, value in gates.items() if value is not True]
    return {
        "registry_id": registry_id,
        "isin": isin,
        "exchange": yahoo_row.get("exchange"),
        "exchange_ticker": yahoo_row.get("exchange_ticker"),
        "trading_currency": yahoo_row.get("trading_currency"),
        "yahoo_symbol": yahoo_row.get("yahoo_symbol"),
        "issuer": issuer.get("issuer") if isinstance(issuer, dict) else None,
        "issuer_product_name": issuer.get("product_name") if isinstance(issuer, dict) else None,
        "issuer_product_url": issuer.get("product_url") if isinstance(issuer, dict) else None,
        "issuer_fetch": {
            "http_status": fetch.get("http_status"),
            "final_url": fetch.get("final_url"),
            "content_type": fetch.get("content_type"),
            "bytes_sampled": fetch.get("bytes_sampled"),
            "fetch_error": fetch.get("fetch_error"),
            "body_sample": compact_sample(text),
        },
        "identity_token_matches": token_matches,
        "gates": gates,
        "failed_gates": failed,
        "issuer_reference_sanity_passed": len(failed) == 0,
        "diagnostic_status": "issuer_reference_blocked" if failed else "issuer_reference_passed",
        "notes": "Issuer page identity is reference evidence only. Reference price/NAV extraction is intentionally not implemented in this gate version.",
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(yahoo_diagnostics: Path, cross_source_gate: Path, issuer_policy: Path, output_dir: Path, run_id: str) -> Path:
    yahoo = load_json(yahoo_diagnostics)
    cross = load_json(cross_source_gate)
    policy = load_yaml(issuer_policy)
    policies = policy_by_registry(policy)
    cross_by_key = {row_key(row): row for row in cross.get("rows", []) if isinstance(row, dict)}
    rows = []
    for row in yahoo.get("rows", []) or []:
        if isinstance(row, dict):
            rows.append(evaluate_row(row, cross_by_key.get(row_key(row)), policies, policy.get("rules") or {}))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_yahoo_diagnostics": str(yahoo_diagnostics),
        "source_cross_source_gate": str(cross_source_gate),
        "issuer_policy": str(issuer_policy),
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "issuer_reference_sanity_passed_count": sum(1 for row in rows if row.get("issuer_reference_sanity_passed") is True),
            "issuer_reference_blocked_count": sum(1 for row in rows if row.get("issuer_reference_sanity_passed") is not True),
            "authority_note": "Issuer reference sanity is diagnostic-only and not a trading-line official close source.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"issuer_reference_sanity_gate_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ISSUER_REFERENCE_SANITY_GATE_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yahoo-diagnostics", required=True)
    parser.add_argument("--cross-source-gate", required=True)
    parser.add_argument("--issuer-policy", default="config/issuer_reference_policy.yml")
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.yahoo_diagnostics), Path(args.cross_source_gate), Path(args.issuer_policy), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
