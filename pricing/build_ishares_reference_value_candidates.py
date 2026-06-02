from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ishares_reference_value_candidates_v1"
TARGET_TOKENS = ["cwpScreenerApi", "productScreenerV3Api"]
TERMS = ["isin", "ticker", "nav", "price", "currency", "date", "fundname"]
TAG_RE = re.compile(r"<([a-zA-Z0-9]+)([^>]*)>")
ATTR_RE = re.compile(r"\s([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=")
CLASS_RE = re.compile(r"class\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
ID_RE = re.compile(r"id\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_text(url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/json,*/*;q=0.8"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(240000)
            return {
                "http_status": getattr(response, "status", None),
                "final_url": getattr(response, "url", url),
                "content_type": response.headers.get("content-type"),
                "bytes_sampled": len(raw),
                "text_sha256": hashlib.sha256(raw).hexdigest(),
                "text": raw.decode("utf-8", errors="replace"),
                "fetch_error": None,
            }
    except Exception as exc:
        return {"http_status": None, "final_url": url, "content_type": None, "bytes_sampled": 0, "text_sha256": None, "text": "", "fetch_error": str(exc)}


def select_targets(parser_probe: dict[str, Any]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in parser_probe.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        token = str(row.get("allowlist_token") or "")
        url = str(row.get("url") or "")
        if token in TARGET_TOKENS and url:
            selected.append({"allowlist_token": token, "url": url})
    selected.sort(key=lambda item: TARGET_TOKENS.index(item["allowlist_token"]))
    return selected


def limited_unique(values: list[str], limit: int = 12) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = re.sub(r"[^A-Za-z0-9_:.#-]", "", value).strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
        if len(result) >= limit:
            break
    return result


def class_tokens(fragment: str) -> list[str]:
    tokens: list[str] = []
    for match in CLASS_RE.finditer(fragment):
        tokens.extend(match.group(1).split())
    return limited_unique(tokens, 10)


def id_tokens(fragment: str) -> list[str]:
    return limited_unique([match.group(1) for match in ID_RE.finditer(fragment)], 10)


def attr_names(fragment: str) -> list[str]:
    return limited_unique([match.group(1).lower() for match in ATTR_RE.finditer(fragment)], 18)


def tag_names(fragment: str) -> list[str]:
    return limited_unique([match.group(1).lower() for match in TAG_RE.finditer(fragment)], 18)


def confidence_for(term: str, fragment: str) -> str:
    lower = fragment.lower()
    structural = any(marker in lower for marker in ["class=", "id=", "data-", "<strong", "<p", "<span", "<div"])
    field_cluster = sum(1 for item in ["isin", "ticker", "nav", "price", "currency", "date"] if item in lower)
    if structural and field_cluster >= 3:
        return "medium"
    if structural or field_cluster >= 2:
        return "low_medium"
    return "low"


def candidates_for_text(text: str) -> list[dict[str, Any]]:
    lower = text.lower()
    candidates: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for term in TERMS:
        positions = [match.start() for match in re.finditer(re.escape(term), lower)][:8]
        for ordinal, pos in enumerate(positions):
            fragment = text[max(0, pos - 450): pos + 450]
            context_hash = hashlib.sha256(fragment.encode("utf-8", errors="ignore")).hexdigest()
            if context_hash in seen_hashes:
                continue
            seen_hashes.add(context_hash)
            candidates.append({
                "candidate_term": term,
                "candidate_kind": "label_or_selector_context",
                "occurrence_ordinal": ordinal,
                "context_sha256": context_hash,
                "nearby_tag_sample": tag_names(fragment),
                "nearby_attribute_name_sample": attr_names(fragment),
                "nearby_class_token_sample": class_tokens(fragment),
                "nearby_id_token_sample": id_tokens(fragment),
                "confidence": confidence_for(term, fragment),
                "raw_value_extracted": False,
                "candidate_value": None,
            })
            if len(candidates) >= 42:
                return candidates
    return candidates


def endpoint_row(target: dict[str, str]) -> dict[str, Any]:
    fetched = fetch_text(target["url"])
    text = str(fetched.get("text") or "")
    candidates = candidates_for_text(text)
    term_counts = {term: sum(1 for item in candidates if item.get("candidate_term") == term) for term in TERMS}
    return {
        "allowlist_token": target["allowlist_token"],
        "url": target["url"],
        "http_status": fetched.get("http_status"),
        "final_url": fetched.get("final_url"),
        "content_type": fetched.get("content_type"),
        "bytes_sampled": fetched.get("bytes_sampled"),
        "text_sha256": fetched.get("text_sha256"),
        "fetch_error": fetched.get("fetch_error"),
        "candidate_count": len(candidates),
        "candidate_term_counts": term_counts,
        "candidates": candidates,
        "answers": {
            "has_nav_or_price_label_candidates": term_counts.get("nav", 0) > 0 or term_counts.get("price", 0) > 0,
            "has_date_or_currency_label_candidates": term_counts.get("date", 0) > 0 or term_counts.get("currency", 0) > 0,
            "has_identity_label_candidates": term_counts.get("isin", 0) > 0 or term_counts.get("ticker", 0) > 0,
            "safe_value_extraction_candidate_next_step": len(candidates) > 0,
        },
        "diagnostic_only": True,
        "reference_price_extraction": "diagnostic_candidate_only_no_values",
        "value_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(parser_probe: Path, output_dir: Path, run_id: str) -> Path:
    source = load_json(parser_probe)
    targets = select_targets(source)
    rows = [endpoint_row(target) for target in targets]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_controlled_parser_probe": str(parser_probe),
        "target_tokens": TARGET_TOKENS,
        "diagnostic_only": True,
        "reference_price_extraction": "diagnostic_candidate_only_no_values",
        "value_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "candidate_count": sum(int(row.get("candidate_count") or 0) for row in rows),
            "rows_with_nav_or_price_candidates": sum(1 for row in rows if row.get("answers", {}).get("has_nav_or_price_label_candidates") is True),
            "rows_with_date_or_currency_candidates": sum(1 for row in rows if row.get("answers", {}).get("has_date_or_currency_label_candidates") is True),
            "authority_note": "Reference value candidates are labels/selectors/context hashes only. No NAV, price, date or currency values are extracted.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ishares_reference_value_candidates_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ISHARES_REFERENCE_VALUE_CANDIDATES_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parser-probe", required=True)
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.parser_probe), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
