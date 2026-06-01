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

SCHEMA_VERSION = "euronext_dynamic_quote_response_discovery_v1"
DEFAULT_OUTPUT_DIR = Path("output/pricing")
DRUPAL_SETTINGS_RE = re.compile(
    r"<script\b[^>]*data-drupal-selector=[\"']drupal-settings-json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_SRC_RE = re.compile(r"<script\b[^>]*src=[\"']([^\"']+)[\"']", re.IGNORECASE)
QUOTED_STRING_RE = re.compile(r"[\"']([^\"']{2,700})[\"']")
RELEVANT_TERMS = ["dynamic_quotes_display", "quote", "quotes", "instrument", "product", "price", "market", "ajax", "api"]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _euronext_rows(product_page_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in product_page_evidence.get("rows", []) if isinstance(row, dict) and row.get("source_id") == "euronext_live"]


def _fetch_text(url: str, max_bytes: int = 70000) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/json;q=0.9,*/*;q=0.8"})
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
    except Exception as exc:  # pragma: no cover - remote provider dependent
        return {"http_status": None, "final_url": url, "content_type": None, "bytes_sampled": 0, "text": "", "fetch_error": str(exc)}


def _extract_drupal_settings(raw: str) -> dict[str, Any] | None:
    match = DRUPAL_SETTINGS_RE.search(raw)
    if not match:
        return None
    payload = html.unescape(match.group(1)).strip()
    if not payload:
        return None
    try:
        loaded = json.loads(payload)
    except json.JSONDecodeError as exc:
        return {"_parse_error": str(exc), "_raw_sample": payload[:500]}
    return loaded if isinstance(loaded, dict) else {"_non_object_settings_type": type(loaded).__name__}


def _dynamic_config(settings: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(settings, dict):
        return {"present": False, "reason": "settings_not_found"}
    dynamic = settings.get("dynamic_quotes_display")
    if not isinstance(dynamic, dict):
        return {"present": False, "reason": "dynamic_quotes_display_not_found"}
    config = dynamic.get("config") if isinstance(dynamic.get("config"), dict) else {}
    return {"present": True, "config": config, "timer": config.get("timer")}


def _walk_endpoint_like_values(value: Any, base_url: str, path: str = "$") -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(_walk_endpoint_like_values(child, base_url, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            found.extend(_walk_endpoint_like_values(child, base_url, f"{path}[{idx}]"))
    elif isinstance(value, str):
        raw = html.unescape(value).replace("\\/", "/").strip()
        lower = raw.lower()
        if raw.startswith(("data:", "javascript:")):
            return found
        if raw.startswith("/") or any(term in lower for term in RELEVANT_TERMS):
            normalized = urllib.parse.urljoin(base_url, raw) if raw.startswith("/") else raw
            found.append({"source": "drupal_settings", "path": path, "url_or_value": normalized[:700]})
    return found


def _script_candidates(text: str, base_url: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in SCRIPT_SRC_RE.finditer(text):
        raw = html.unescape(match.group(1)).strip()
        url = urllib.parse.urljoin(base_url, raw)
        lower = url.lower()
        if not any(term in lower for term in ["quote", "dynamic", "instrument", "product", "market", "euronext"]):
            continue
        if url in seen:
            continue
        seen.add(url)
        candidates.append({"source": "script_src", "url": url})
        if len(candidates) >= 20:
            break
    return candidates


def _inline_context_samples(text: str) -> list[dict[str, str]]:
    samples: list[dict[str, str]] = []
    for term in ["dynamic_quotes_display", "nameInstrument", "product_data", "ajaxTrustedUrl", "ajaxPageState"]:
        for match in re.finditer(re.escape(term), text, flags=re.IGNORECASE):
            context = re.sub(r"\s+", " ", text[max(0, match.start() - 180): match.end() + 260]).strip()
            samples.append({"term": term, "context": context[:700]})
            break
    return samples


def _explicit_response_candidates(settings: dict[str, Any] | None, page_text: str, base_url: str, row: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    if isinstance(settings, dict):
        for item in _walk_endpoint_like_values(settings, base_url):
            value = str(item.get("url_or_value") or "")
            lower = value.lower()
            if not value.startswith("http"):
                continue
            if not any(term in lower for term in ["quote", "price", "instrument", "product", "market", "ajax"]):
                continue
            if value in seen:
                continue
            seen.add(value)
            candidates.append({"name": "settings_discovered_endpoint", "source": item.get("source"), "path": item.get("path"), "url": value})
    for match in QUOTED_STRING_RE.finditer(page_text):
        raw = html.unescape(match.group(1)).replace("\\/", "/").strip()
        lower = raw.lower()
        if not raw.startswith("/"):
            continue
        if not any(term in lower for term in ["quote", "price", "instrument", "product", "market", "ajax"]):
            continue
        url = urllib.parse.urljoin(base_url, raw)
        if url in seen:
            continue
        seen.add(url)
        candidates.append({"name": "inline_discovered_endpoint", "source": "inline_quoted_string", "url": url})
        if len(candidates) >= 30:
            break
    return candidates[:30]


def _sample_single_explicit_candidate(candidates: list[dict[str, Any]], row: dict[str, Any]) -> dict[str, Any]:
    """Sample at most one explicitly discovered endpoint. Never parse prices."""
    fetchable = [item for item in candidates if str(item.get("url") or "").startswith("http")]
    if not fetchable:
        return {"fetch_attempted": False, "reason": "no_explicit_fetchable_candidate"}
    target = fetchable[0]
    fetched = _fetch_text(str(target.get("url")), max_bytes=10000)
    text = fetched.get("text") or ""
    lower = text.lower()
    sample = {
        "fetch_attempted": True,
        "target": target,
        "http_status": fetched.get("http_status"),
        "final_url": fetched.get("final_url"),
        "content_type": fetched.get("content_type"),
        "bytes_sampled": fetched.get("bytes_sampled"),
        "fetch_error": fetched.get("fetch_error"),
        "looks_json": text.lstrip().startswith(("{", "[")),
        "contains_isin": str(row.get("isin") or "").lower() in lower,
        "contains_exchange_ticker": str(row.get("exchange_ticker") or "").lower() in lower,
        "contains_provider_symbol": str(row.get("provider_symbol") or "").lower() in lower,
        "contains_quote_terms": any(term in lower for term in ["quote", "price", "last", "close", "currency", "time"]),
        "body_sample": re.sub(r"\s+", " ", text[:900]).strip(),
        "candidate_close_extraction": False,
        "completed_session_validation": False,
    }
    return sample


def _row_discovery(row: dict[str, Any]) -> dict[str, Any]:
    source_url = str(row.get("source_url") or "")
    product_fetch = _fetch_text(source_url, max_bytes=70000)
    page_text = product_fetch.get("text") or ""
    final_url = str(product_fetch.get("final_url") or source_url)
    settings = _extract_drupal_settings(page_text)
    dynamic = _dynamic_config(settings)
    settings_endpoints = _walk_endpoint_like_values(settings, final_url) if isinstance(settings, dict) else []
    script_candidates = _script_candidates(page_text, final_url)
    explicit_candidates = _explicit_response_candidates(settings, page_text, final_url, row)
    sampled = _sample_single_explicit_candidate(explicit_candidates, row)
    response_status = "explicit_response_candidate_sampled" if sampled.get("fetch_attempted") else "no_explicit_dynamic_response_endpoint_found"
    return {
        "registry_id": row.get("registry_id"),
        "isin": row.get("isin"),
        "exchange_ticker": row.get("exchange_ticker"),
        "provider_symbol": row.get("provider_symbol"),
        "source_id": row.get("source_id"),
        "source_url": source_url,
        "discovery_status": response_status,
        "product_page_fetch": {
            "http_status": product_fetch.get("http_status"),
            "final_url": product_fetch.get("final_url"),
            "content_type": product_fetch.get("content_type"),
            "bytes_sampled": product_fetch.get("bytes_sampled"),
            "fetch_error": product_fetch.get("fetch_error"),
        },
        "dynamic_quotes_display": dynamic,
        "settings_endpoint_like_values": settings_endpoints[:30],
        "script_src_candidates": script_candidates[:20],
        "inline_context_samples": _inline_context_samples(page_text),
        "explicit_response_candidates": explicit_candidates,
        "sampled_response_evidence": sampled,
        "answers": {
            "which_endpoint_or_response_is_triggered": "not_explicit_in_product_page_settings" if not explicit_candidates else "explicit_candidate_detected_in_page_or_settings",
            "does_it_return_structured_quote_data": bool(sampled.get("looks_json")) if sampled.get("fetch_attempted") else False,
            "does_it_preserve_verified_product_identity": bool(sampled.get("contains_isin") and sampled.get("contains_provider_symbol")) if sampled.get("fetch_attempted") else False,
        },
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(product_page_evidence_path: Path, output_dir: Path, run_id: str) -> Path:
    product_page_evidence = _load_json(product_page_evidence_path)
    rows = [_row_discovery(row) for row in _euronext_rows(product_page_evidence)]
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(product_page_evidence_path),
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
    path = output_dir / f"euronext_dynamic_quote_response_discovery_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(f"EURONEXT_DYNAMIC_QUOTE_RESPONSE_DISCOVERY_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-page-evidence", required=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.product_page_evidence), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
