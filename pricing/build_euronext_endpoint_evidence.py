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

SCHEMA_VERSION = "euronext_endpoint_evidence_v1"
TARGET_CANDIDATE_NAME = "settings_search_product_data"
DEFAULT_OUTPUT_DIR = Path("output/pricing")
HREF_RE = re.compile(r"href=[\"']([^\"']+)[\"']", re.IGNORECASE)
CANONICAL_RE = re.compile(r"<link\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)[\"']", re.IGNORECASE)
CANONICAL_RE_REVERSED = re.compile(r"<link\b[^>]*href=[\"']([^\"']+)[\"'][^>]*rel=[\"']canonical[\"']", re.IGNORECASE)


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


def _fetch_sample(url: str, row: dict[str, Any]) -> dict[str, Any]:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(25000)
            text = raw.decode("utf-8", errors="replace")
            final_url = getattr(response, "url", None)
            return {
                "http_status": getattr(response, "status", None),
                "final_url": final_url,
                "content_type": response.headers.get("content-type"),
                "bytes_sampled": len(raw),
                "body_sample": re.sub(r"\s+", " ", text[:900]).strip(),
                "html_inspection": _inspect_html(text, base_url=final_url or url, target_url=url, row=row),
                "fetch_error": None,
            }
    except Exception as exc:  # pragma: no cover - provider dependent
        return {
            "http_status": None,
            "final_url": url,
            "content_type": None,
            "bytes_sampled": 0,
            "body_sample": "",
            "html_inspection": {"inspection_status": "fetch_failed"},
            "fetch_error": str(exc),
        }


def _canonical_url(text: str, base_url: str) -> str | None:
    for pattern in [CANONICAL_RE, CANONICAL_RE_REVERSED]:
        match = pattern.search(text)
        if match:
            return urllib.parse.urljoin(base_url, html.unescape(match.group(1).strip()))
    return None


def _href_candidates(text: str, base_url: str, row: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    seen: set[str] = set()
    identity_tokens = [str(row.get("isin") or ""), str(row.get("provider_symbol") or ""), str(row.get("exchange_ticker") or "")]
    for match in HREF_RE.finditer(text):
        raw_value = html.unescape(match.group(1)).strip()
        normalized = urllib.parse.urljoin(base_url, raw_value)
        lower = normalized.lower()
        if not any(token and token.lower() in lower for token in identity_tokens):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        values.append({
            "url": normalized,
            "is_product_page": "/product/" in lower,
            "is_search_page": "/search_instruments/" in lower,
            "contains_isin": str(row.get("isin") or "").lower() in lower,
            "contains_provider_symbol": str(row.get("provider_symbol") or "").lower() in lower,
            "contains_exchange_ticker": str(row.get("exchange_ticker") or "").lower() in lower,
        })
        if len(values) >= 20:
            break
    return values


def _term_counts(text: str) -> dict[str, int]:
    lower = text.lower()
    terms = [
        "views-row",
        "search-result",
        "instrument",
        "product/etfs",
        "search_instruments",
        "dynamic_quotes_display",
        "product_data",
        "last price",
        "closing price",
        "isin",
    ]
    return {term: lower.count(term) for term in terms}


def _inspect_html(text: str, base_url: str, target_url: str, row: dict[str, Any]) -> dict[str, Any]:
    canonical = _canonical_url(text, base_url)
    hrefs = _href_candidates(text, base_url, row)
    product_links = [item for item in hrefs if item.get("is_product_page")]
    search_links = [item for item in hrefs if item.get("is_search_page")]
    target_normalized = urllib.parse.urljoin(base_url, target_url)
    canonical_is_target = canonical == target_normalized
    return {
        "inspection_status": "html_inspected",
        "canonical_url": canonical,
        "canonical_is_target_url": canonical_is_target,
        "identity_href_count": len(hrefs),
        "identity_href_candidates": hrefs[:12],
        "product_link_count": len(product_links),
        "product_link_candidates": product_links[:10],
        "search_link_count": len(search_links),
        "search_link_candidates": search_links[:10],
        "term_counts": _term_counts(text),
        "contains_product_card_structure": bool(product_links or re.search(r"views-row|search-result|instrument", text, flags=re.IGNORECASE)),
        "search_endpoint_loops_to_search_page": bool(canonical_is_target and not product_links),
        "recommended_next_step": "stop_search_endpoint_path_and_focus_product_page_parser" if canonical_is_target and not product_links else "inspect_product_link_candidates_before_parser_design",
        "diagnostic_only": True,
    }


def _signals(sample: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    text = str(sample.get("body_sample") or "")
    lower = text.lower()
    html_inspection = sample.get("html_inspection") if isinstance(sample.get("html_inspection"), dict) else {}
    return {
        "contains_isin": str(row.get("isin") or "").lower() in lower,
        "contains_exchange_ticker": str(row.get("exchange_ticker") or "").lower() in lower,
        "contains_provider_symbol": str(row.get("provider_symbol") or "").lower() in lower,
        "contains_quote_terms": any(term in lower for term in ["quote", "price", "last", "close", "currency"]),
        "looks_json": text.lstrip().startswith(("{", "[")),
        "product_link_count": html_inspection.get("product_link_count"),
        "search_endpoint_loops_to_search_page": html_inspection.get("search_endpoint_loops_to_search_page"),
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
        sample = _fetch_sample(candidate["url"], row)
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
