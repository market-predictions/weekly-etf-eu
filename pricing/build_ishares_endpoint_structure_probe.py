from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ishares_endpoint_structure_probe_v1"
TARGET_TOKENS = ["cwpScreenerApi", "productScreenerV3Api"]
LABEL_TERMS = ["isin", "ticker", "nav", "currency", "asof", "date", "fundname", "productname", "price"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_text(url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/json,*/*;q=0.8"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(220000)
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


def select_targets(endpoint_evidence: dict[str, Any]) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in endpoint_evidence.get("endpoints", []) or []:
        if not isinstance(item, dict):
            continue
        token = str(item.get("allowlist_token") or "")
        url = str(item.get("url") or "")
        if token in TARGET_TOKENS and url and token not in seen:
            seen.add(token)
            targets.append({"allowlist_token": token, "url": url})
    targets.sort(key=lambda item: TARGET_TOKENS.index(item["allowlist_token"]))
    return targets


def count_patterns(text: str) -> dict[str, int]:
    lower = text.lower()
    return {
        "script_tag_count": len(re.findall(r"<script\b", text, flags=re.IGNORECASE)),
        "table_tag_count": len(re.findall(r"<table\b", text, flags=re.IGNORECASE)),
        "row_tag_count": len(re.findall(r"<tr\b", text, flags=re.IGNORECASE)),
        "json_script_type_count": len(re.findall(r"type=[\"']application/(?:ld\+)?json[\"']", text, flags=re.IGNORECASE)),
        "brace_pairs_approx": min(lower.count("{"), lower.count("}")),
        "data_attribute_count": len(re.findall(r"\sdata-[a-z0-9_-]+=", text, flags=re.IGNORECASE)),
        "next_data_marker_count": lower.count("__next_data__"),
        "drupal_settings_marker_count": lower.count("drupal.settings") + lower.count("drupalsettings"),
    }


def label_counts(text: str) -> dict[str, int]:
    lower = text.lower()
    return {term: lower.count(term) for term in LABEL_TERMS}


def structure_signals(text: str) -> dict[str, bool]:
    counts = count_patterns(text)
    labels = label_counts(text)
    return {
        "has_embedded_json_like_blocks": counts["json_script_type_count"] > 0 or counts["brace_pairs_approx"] > 20,
        "has_table_like_structure": counts["table_tag_count"] > 0 or counts["row_tag_count"] > 5,
        "has_data_attributes": counts["data_attribute_count"] > 10,
        "has_nav_or_price_label_signal": labels.get("nav", 0) > 0 or labels.get("price", 0) > 0,
        "has_date_or_currency_label_signal": labels.get("date", 0) > 0 or labels.get("currency", 0) > 0 or labels.get("asof", 0) > 0,
        "has_identity_label_signal": labels.get("isin", 0) > 0 or labels.get("ticker", 0) > 0,
    }


def probe_target(target: dict[str, str], expected_isin: str) -> dict[str, Any]:
    fetched = fetch_text(target["url"])
    text = str(fetched.get("text") or "")
    signals = structure_signals(text)
    counts = count_patterns(text)
    labels = label_counts(text)
    return {
        "allowlist_token": target["allowlist_token"],
        "url": target["url"],
        "http_status": fetched.get("http_status"),
        "final_url": fetched.get("final_url"),
        "content_type": fetched.get("content_type"),
        "bytes_sampled": fetched.get("bytes_sampled"),
        "fetch_error": fetched.get("fetch_error"),
        "expected_isin_present": bool(expected_isin and expected_isin.lower() in text.lower()),
        "structure_counts": counts,
        "label_counts": labels,
        "signals": signals,
        "answers": {
            "worth_controlled_parser_followup": bool(signals["has_embedded_json_like_blocks"] or signals["has_table_like_structure"] or signals["has_data_attributes"]),
            "issuer_reference_structure_observed": bool(signals["has_identity_label_signal"] and (signals["has_nav_or_price_label_signal"] or signals["has_date_or_currency_label_signal"])),
        },
        "diagnostic_only": True,
        "reference_price_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def expected_isin_from_policy(path: Path) -> str:
    if not path.exists():
        return ""
    match = re.search(r"isin:\s*([A-Z0-9]+)", path.read_text(encoding="utf-8"))
    return match.group(1) if match else ""


def build(endpoint_evidence: Path, issuer_policy: Path, output_dir: Path, run_id: str) -> Path:
    evidence = load_json(endpoint_evidence)
    expected_isin = expected_isin_from_policy(issuer_policy)
    targets = select_targets(evidence)
    rows = [probe_target(target, expected_isin) for target in targets]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_endpoint_evidence": str(endpoint_evidence),
        "issuer_policy": str(issuer_policy),
        "target_tokens": TARGET_TOKENS,
        "diagnostic_only": True,
        "reference_price_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "controlled_parser_followup_count": sum(1 for row in rows if row.get("answers", {}).get("worth_controlled_parser_followup") is True),
            "issuer_reference_structure_count": sum(1 for row in rows if row.get("answers", {}).get("issuer_reference_structure_observed") is True),
            "authority_note": "Structure probe is diagnostic-only. It detects structures and labels but does not extract reference-price, NAV, dates or currency values.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ishares_endpoint_structure_probe_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ISHARES_ENDPOINT_STRUCTURE_PROBE_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint-evidence", required=True)
    parser.add_argument("--issuer-policy", default="config/issuer_reference_policy.yml")
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.endpoint_evidence), Path(args.issuer_policy), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
