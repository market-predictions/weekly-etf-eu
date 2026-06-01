from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "ishares_endpoint_evidence_v1"
ALLOWLIST = ["product-data.jsn", "product-screener-v3.jsn", "cwpScreenerApi", "productScreenerV3Api"]
FIELD_GROUPS = {
    "isin": ["isin"],
    "product_name": ["productname", "fundname", "displayname"],
    "ticker": ["ticker", "localticker"],
    "nav": ["nav", "netassetvalue", "navprice"],
    "reference_date": ["asofdate", "lastupdated", "effectivedate"],
    "currency": ["currency", "basecurrency", "localcurrency"],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def allow_token(url: str) -> str | None:
    lower = url.lower()
    for token in ALLOWLIST:
        if token.lower() in lower:
            return token
    return None


def fetch_text(url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*;q=0.8"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(160000)
            return {
                "http_status": getattr(response, "status", None),
                "final_url": getattr(response, "url", url),
                "content_type": response.headers.get("content-type"),
                "bytes_sampled": len(raw),
                "text": raw.decode("utf-8", errors="replace"),
                "fetch_error": None,
            }
    except Exception as exc:
        return {"http_status": None, "final_url": url, "content_type": None, "bytes_sampled": 0, "text": "", "fetch_error": str(exc)}


def select_candidates(discovery: dict[str, Any]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen_tokens: set[str] = set()
    for row in discovery.get("rows", []) or []:
        for candidate in row.get("endpoint_candidates", []) or []:
            if not isinstance(candidate, dict):
                continue
            url = str(candidate.get("url") or "")
            token = allow_token(url)
            if token and token not in seen_tokens:
                seen_tokens.add(token)
                selected.append({"allowlist_token": token, "url": url})
    selected.sort(key=lambda item: ALLOWLIST.index(item["allowlist_token"]))
    return selected


def flatten_keys(value: Any, prefix: str = "") -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            keys.append(path)
            keys.extend(flatten_keys(child, path))
    elif isinstance(value, list):
        for child in value[:2]:
            keys.extend(flatten_keys(child, prefix + "[]"))
    return keys[:300]


def field_groups_present(text: str, keys: list[str]) -> dict[str, bool]:
    haystack = (text + "\n" + "\n".join(keys)).lower()
    return {group: any(term in haystack for term in terms) for group, terms in FIELD_GROUPS.items()}


def inspect_endpoint(item: dict[str, str], expected_tokens: list[str]) -> dict[str, Any]:
    fetched = fetch_text(item["url"])
    text = str(fetched.get("text") or "")
    parsed = None
    json_error = None
    try:
        parsed = json.loads(text) if text.strip() else None
    except Exception as exc:
        json_error = str(exc)
    keys = flatten_keys(parsed) if parsed is not None else []
    token_presence = {token: (token.lower() in text.lower()) for token in expected_tokens}
    fields = field_groups_present(text, keys)
    return {
        "allowlist_token": item["allowlist_token"],
        "url": item["url"],
        "http_status": fetched.get("http_status"),
        "final_url": fetched.get("final_url"),
        "content_type": fetched.get("content_type"),
        "bytes_sampled": fetched.get("bytes_sampled"),
        "fetch_error": fetched.get("fetch_error"),
        "returns_json": parsed is not None,
        "json_parse_error": json_error,
        "json_key_count_sampled": len(keys),
        "field_groups_present": fields,
        "expected_token_presence": token_presence,
        "answers": {
            "structured_data_observed": parsed is not None,
            "isin_signal_observed": fields.get("isin") is True,
            "product_or_ticker_signal_observed": fields.get("product_name") is True or fields.get("ticker") is True,
            "nav_date_or_currency_field_signal_observed": fields.get("nav") is True or fields.get("reference_date") is True or fields.get("currency") is True,
        },
        "diagnostic_only": True,
        "reference_price_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(endpoint_discovery: Path, issuer_policy: Path, output_dir: Path, run_id: str) -> Path:
    discovery = load_json(endpoint_discovery)
    policy = load_yaml(issuer_policy)
    products = policy.get("issuer_products") or []
    expected_tokens: list[str] = []
    for product in products:
        if isinstance(product, dict):
            expected_tokens.extend(str(token) for token in product.get("expected_tokens") or [])
            if product.get("isin"):
                expected_tokens.append(str(product.get("isin")))
    candidates = select_candidates(discovery)
    endpoints = [inspect_endpoint(item, expected_tokens) for item in candidates]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_endpoint_discovery": str(endpoint_discovery),
        "issuer_policy": str(issuer_policy),
        "allowlist": ALLOWLIST,
        "diagnostic_only": True,
        "reference_price_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "endpoints": endpoints,
        "summary": {
            "endpoint_count": len(endpoints),
            "json_endpoint_count": sum(1 for row in endpoints if row.get("returns_json") is True),
            "isin_signal_count": sum(1 for row in endpoints if row.get("answers", {}).get("isin_signal_observed") is True),
            "nav_date_or_currency_signal_count": sum(1 for row in endpoints if row.get("answers", {}).get("nav_date_or_currency_field_signal_observed") is True),
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ishares_endpoint_evidence_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ISHARES_ENDPOINT_EVIDENCE_OK | artifact={path} | endpoints={len(endpoints)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint-discovery", required=True)
    parser.add_argument("--issuer-policy", default="config/issuer_reference_policy.yml")
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.endpoint_discovery), Path(args.issuer_policy), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
