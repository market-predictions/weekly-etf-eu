from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "ishares_reference_endpoint_discovery_v1"
RELEVANT_TERMS = ["fund", "product", "nav", "price", "performance", "holdings", "factsheet", "download", "ajax", "api", "chart"]
HREF_RE = re.compile(r"href=[\"']([^\"']+)[\"']", re.IGNORECASE)
SRC_RE = re.compile(r"src=[\"']([^\"']+)[\"']", re.IGNORECASE)
QUOTED_RE = re.compile(r"[\"']([^\"']{3,700})[\"']")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def fetch_text(url: str, max_bytes: int = 150000) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/json,*/*;q=0.8"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(max_bytes)
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


def compact(value: str, limit: int = 900) -> str:
    return re.sub(r"\s+", " ", html.unescape(value[:limit])).strip()


def is_relevant(value: str) -> bool:
    lower = value.lower()
    return any(term in lower for term in RELEVANT_TERMS) or value.lower().endswith((".json", ".csv", ".xlsx", ".pdf"))


def normalize(base_url: str, value: str) -> str:
    value = html.unescape(value).replace("\\/", "/").strip()
    return urllib.parse.urljoin(base_url, value)


def collect_candidates(text: str, base_url: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_name, pattern in [("href", HREF_RE), ("src", SRC_RE), ("quoted_string", QUOTED_RE)]:
        for match in pattern.finditer(text):
            raw = match.group(1).strip()
            if not raw or raw.startswith(("data:", "javascript:", "mailto:", "#")):
                continue
            if not (raw.startswith("/") or raw.startswith("http") or is_relevant(raw)):
                continue
            url = normalize(base_url, raw)
            if not is_relevant(url) and not is_relevant(raw):
                continue
            if url in seen:
                continue
            seen.add(url)
            lower = url.lower()
            candidates.append({
                "source": source_name,
                "url": url,
                "looks_api_or_json": any(token in lower for token in ["api", "ajax", ".json"]),
                "looks_document": any(token in lower for token in ["factsheet", ".pdf", ".xlsx", ".csv"]),
                "looks_nav_or_price_related": any(token in lower for token in ["nav", "price", "performance", "chart"]),
            })
            if len(candidates) >= 80:
                return candidates
    return candidates


def context_samples(text: str) -> list[dict[str, str]]:
    samples: list[dict[str, str]] = []
    for term in ["isin", "nav", "price", "performance", "factsheet", "api", "ajax", "fund"]:
        match = re.search(re.escape(term), text, flags=re.IGNORECASE)
        if match:
            samples.append({"term": term, "context": compact(text[max(0, match.start() - 220): match.end() + 320])})
    return samples[:20]


def evaluate_product(product: dict[str, Any]) -> dict[str, Any]:
    url = str(product.get("product_url") or "")
    fetched = fetch_text(url)
    text = str(fetched.get("text") or "")
    final_url = str(fetched.get("final_url") or url)
    candidates = collect_candidates(text, final_url)
    tokens = [str(token) for token in product.get("expected_tokens") or []]
    token_presence = {token: (token.lower() in text.lower()) for token in tokens}
    return {
        "registry_id": product.get("registry_id"),
        "isin": product.get("isin"),
        "issuer": product.get("issuer"),
        "product_name": product.get("product_name"),
        "product_url": url,
        "page_fetch": {
            "http_status": fetched.get("http_status"),
            "final_url": fetched.get("final_url"),
            "content_type": fetched.get("content_type"),
            "bytes_sampled": fetched.get("bytes_sampled"),
            "fetch_error": fetched.get("fetch_error"),
        },
        "token_presence": token_presence,
        "candidate_count": len(candidates),
        "endpoint_candidates": candidates,
        "context_samples": context_samples(text),
        "answers": {
            "stable_endpoint_found": any(item.get("looks_api_or_json") for item in candidates),
            "factsheet_or_document_candidate_found": any(item.get("looks_document") for item in candidates),
            "nav_or_price_related_candidate_found": any(item.get("looks_nav_or_price_related") for item in candidates),
        },
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "reference_price_extraction": False,
    }


def build(issuer_policy: Path, output_dir: Path, run_id: str) -> Path:
    policy = load_yaml(issuer_policy)
    rows = [evaluate_product(product) for product in policy.get("issuer_products", []) or [] if isinstance(product, dict)]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "issuer_policy": str(issuer_policy),
        "diagnostic_only": True,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "reference_price_extraction": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "products_with_endpoint_candidates": sum(1 for row in rows if int(row.get("candidate_count") or 0) > 0),
            "products_with_api_or_json_candidates": sum(1 for row in rows if row.get("answers", {}).get("stable_endpoint_found") is True),
            "authority_note": "Endpoint discovery is diagnostic-only and cannot create issuer reference price, NAV, valuation authority or Yahoo fallback authority.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ishares_reference_endpoint_discovery_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ISHARES_REFERENCE_ENDPOINT_DISCOVERY_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issuer-policy", default="config/issuer_reference_policy.yml")
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.issuer_policy), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
