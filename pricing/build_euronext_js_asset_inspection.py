from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "euronext_js_asset_inspection_v1"
DEFAULT_OUTPUT_DIR = Path("output/pricing")
SEARCH_TERMS = ["dynamic_quotes_display", "quote", "quotes", "last", "close", "price", "instrument", "product_data", "ajax"]
ROUTE_RE = re.compile(r"[\"']([^\"']{2,500})[\"']")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _euronext_rows(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in discovery.get("rows", []) if isinstance(row, dict) and row.get("source_id") == "euronext_live"]


def _fetch_text(url: str, max_bytes: int = 120000) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/javascript,text/javascript,*/*;q=0.8"})
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(max_bytes)
            text = raw.decode("utf-8", errors="replace")
            return {
                "http_status": getattr(response, "status", None),
                "final_url": getattr(response, "url", None),
                "content_type": response.headers.get("content-type"),
                "bytes_sampled": len(raw),
                "text": text,
                "fetch_error": None,
            }
    except Exception as exc:  # pragma: no cover - provider dependent
        return {"http_status": None, "final_url": url, "content_type": None, "bytes_sampled": 0, "text": "", "fetch_error": str(exc)}


def _term_counts(text: str) -> dict[str, int]:
    lower = text.lower()
    return {term: lower.count(term.lower()) for term in SEARCH_TERMS}


def _context_samples(text: str) -> list[dict[str, str]]:
    samples: list[dict[str, str]] = []
    for term in SEARCH_TERMS:
        for match in re.finditer(re.escape(term), text, flags=re.IGNORECASE):
            context = re.sub(r"\s+", " ", text[max(0, match.start() - 180): match.end() + 260]).strip()
            samples.append({"term": term, "context": context[:900]})
            break
    return samples[:20]


def _route_candidates(text: str, base_url: str) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()
    for match in ROUTE_RE.finditer(text):
        raw = match.group(1).replace("\\/", "/").strip()
        lower = raw.lower()
        if raw.startswith(("data:", "javascript:")):
            continue
        if not (raw.startswith("/") or any(term in lower for term in ["quote", "price", "instrument", "product", "market", "ajax", "chart"])):
            continue
        value = urllib.parse.urljoin(base_url, raw) if raw.startswith("/") else raw
        if value in seen:
            continue
        seen.add(value)
        candidates.append({"value": value, "absolute_url": value if value.startswith("http") else "", "source": "quoted_js_string"})
        if len(candidates) >= 40:
            break
    return candidates


def _asset_inspection(asset: dict[str, Any], source_url: str) -> dict[str, Any]:
    url = str(asset.get("url") or "")
    fetched = _fetch_text(url)
    text = fetched.get("text") or ""
    base_url = fetched.get("final_url") or url or source_url
    return {
        "asset_url": url,
        "http_status": fetched.get("http_status"),
        "final_url": fetched.get("final_url"),
        "content_type": fetched.get("content_type"),
        "bytes_sampled": fetched.get("bytes_sampled"),
        "fetch_error": fetched.get("fetch_error"),
        "term_counts": _term_counts(text),
        "context_samples": _context_samples(text),
        "route_candidates": _route_candidates(text, base_url),
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "authority": False,
    }


def _row_inspection(row: dict[str, Any]) -> dict[str, Any]:
    assets = row.get("script_src_candidates") if isinstance(row.get("script_src_candidates"), list) else []
    inspected = [_asset_inspection(asset, str(row.get("source_url") or "")) for asset in assets[:6] if isinstance(asset, dict)]
    route_candidates: list[dict[str, str]] = []
    for item in inspected:
        route_candidates.extend(item.get("route_candidates") or [])
    meaningful_routes = [item for item in route_candidates if any(term in str(item.get("value") or "").lower() for term in ["quote", "price", "instrument", "chart", "market"])]
    return {
        "registry_id": row.get("registry_id"),
        "isin": row.get("isin"),
        "exchange_ticker": row.get("exchange_ticker"),
        "provider_symbol": row.get("provider_symbol"),
        "source_id": row.get("source_id"),
        "source_url": row.get("source_url"),
        "inspection_status": "js_assets_inspected" if inspected else "no_js_assets_to_inspect",
        "asset_count": len(assets),
        "inspected_asset_count": len(inspected),
        "assets": inspected,
        "meaningful_route_candidate_count": len(meaningful_routes),
        "meaningful_route_candidates": meaningful_routes[:30],
        "answers": {
            "dynamic_behavior_found_in_js": any((asset.get("term_counts") or {}).get("dynamic_quotes_display", 0) > 0 for asset in inspected),
            "quote_or_price_route_candidate_found": bool(meaningful_routes),
            "route_sampled": False,
        },
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(dynamic_discovery_path: Path, output_dir: Path, run_id: str) -> Path:
    discovery = _load_json(dynamic_discovery_path)
    rows = [_row_inspection(row) for row in _euronext_rows(discovery)]
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(dynamic_discovery_path),
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
    path = output_dir / f"euronext_js_asset_inspection_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"EURONEXT_JS_ASSET_INSPECTION_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dynamic-discovery", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.dynamic_discovery), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
