from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "ishares_controlled_parser_probe_v1"
TARGET_TOKENS = ["cwpScreenerApi", "productScreenerV3Api"]
TERMS = ["isin", "ticker", "nav", "price", "currency", "date", "fundname", "productname"]
ATTR_RE = re.compile(r"\s([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=")
TAG_RE = re.compile(r"<([a-zA-Z0-9]+)([^>]*)>")
CLASS_RE = re.compile(r"class\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
ID_RE = re.compile(r"id\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script\b([^>]*)>", re.IGNORECASE)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_text(url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html,application/json,*/*;q=0.8"})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(240000)
            text = raw.decode("utf-8", errors="replace")
            return {
                "http_status": getattr(response, "status", None),
                "final_url": getattr(response, "url", url),
                "content_type": response.headers.get("content-type"),
                "bytes_sampled": len(raw),
                "text_sha256": hashlib.sha256(raw).hexdigest(),
                "text": text,
                "fetch_error": None,
            }
    except Exception as exc:
        return {"http_status": None, "final_url": url, "content_type": None, "bytes_sampled": 0, "text_sha256": None, "text": "", "fetch_error": str(exc)}


def select_targets(structure_probe: dict[str, Any]) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    for row in structure_probe.get("rows", []) or []:
        if not isinstance(row, dict):
            continue
        token = str(row.get("allowlist_token") or "")
        url = str(row.get("url") or "")
        if token in TARGET_TOKENS and url:
            targets.append({"allowlist_token": token, "url": url})
    targets.sort(key=lambda item: TARGET_TOKENS.index(item["allowlist_token"]))
    return targets


def unique_limited(values: list[str], limit: int = 40) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = re.sub(r"[^A-Za-z0-9_:.#-]", "", value).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= limit:
            break
    return result


def attribute_names(text: str) -> list[str]:
    return unique_limited([match.group(1).lower() for match in ATTR_RE.finditer(text)], 60)


def script_attribute_names(text: str) -> list[str]:
    names: list[str] = []
    for match in SCRIPT_RE.finditer(text):
        names.extend(attr.group(1).lower() for attr in ATTR_RE.finditer(match.group(1)))
    return unique_limited(names, 30)


def class_token_sample(text: str) -> list[str]:
    tokens: list[str] = []
    for match in CLASS_RE.finditer(text):
        tokens.extend(match.group(1).split())
    return unique_limited(tokens, 50)


def id_token_sample(text: str) -> list[str]:
    return unique_limited([match.group(1) for match in ID_RE.finditer(text)], 50)


def tag_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in TAG_RE.finditer(text):
        tag = match.group(1).lower()
        counts[tag] = counts.get(tag, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:30])


def term_context_shapes(text: str) -> dict[str, dict[str, Any]]:
    lower = text.lower()
    shapes: dict[str, dict[str, Any]] = {}
    for term in TERMS:
        positions = [m.start() for m in re.finditer(re.escape(term), lower)][:12]
        nearby_tags: list[str] = []
        nearby_attrs: list[str] = []
        for pos in positions[:5]:
            window = text[max(0, pos - 300): pos + 300]
            nearby_tags.extend(match.group(1).lower() for match in TAG_RE.finditer(window))
            nearby_attrs.extend(match.group(1).lower() for match in ATTR_RE.finditer(window))
        shapes[term] = {
            "occurrence_count_limited": len(positions),
            "nearby_tag_sample": unique_limited(nearby_tags, 20),
            "nearby_attribute_name_sample": unique_limited(nearby_attrs, 20),
        }
    return shapes


def parser_signals(text: str) -> dict[str, bool]:
    classes = class_token_sample(text)
    ids = id_token_sample(text)
    attrs = attribute_names(text)
    lower_name_space = " ".join(classes + ids + attrs).lower()
    lower_text = text.lower()
    has_labels = all(term in lower_text for term in ["isin", "nav", "currency"])
    has_selector_tokens = any(token in lower_name_space for token in ["fund", "product", "price", "nav", "screener", "data-"])
    has_structures = lower_text.count("{") > 20 or "data-" in lower_text or "<script" in lower_text
    return {
        "stable_selector_candidate_observed": bool(has_selector_tokens and has_structures),
        "parser_followup_worthwhile": bool(has_labels and has_selector_tokens and has_structures),
        "value_extraction_still_blocked": True,
    }


def probe(target: dict[str, str]) -> dict[str, Any]:
    fetched = fetch_text(target["url"])
    text = str(fetched.get("text") or "")
    return {
        "allowlist_token": target["allowlist_token"],
        "url": target["url"],
        "http_status": fetched.get("http_status"),
        "final_url": fetched.get("final_url"),
        "content_type": fetched.get("content_type"),
        "bytes_sampled": fetched.get("bytes_sampled"),
        "text_sha256": fetched.get("text_sha256"),
        "fetch_error": fetched.get("fetch_error"),
        "tag_counts_top": tag_counts(text),
        "attribute_name_sample": attribute_names(text),
        "script_attribute_name_sample": script_attribute_names(text),
        "class_token_sample": class_token_sample(text),
        "id_token_sample": id_token_sample(text),
        "term_context_shapes": term_context_shapes(text),
        "signals": parser_signals(text),
        "diagnostic_only": True,
        "reference_price_extraction": False,
        "value_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
    }


def build(structure_probe: Path, output_dir: Path, run_id: str) -> Path:
    source = load_json(structure_probe)
    targets = select_targets(source)
    rows = [probe(target) for target in targets]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_structure_probe": str(structure_probe),
        "target_tokens": TARGET_TOKENS,
        "diagnostic_only": True,
        "reference_price_extraction": False,
        "value_extraction": False,
        "valuation_authority": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery": False,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "parser_followup_worthwhile_count": sum(1 for row in rows if row.get("signals", {}).get("parser_followup_worthwhile") is True),
            "stable_selector_candidate_count": sum(1 for row in rows if row.get("signals", {}).get("stable_selector_candidate_observed") is True),
            "authority_note": "Controlled parser probe records selector and structure signals only. It does not extract NAV, price, date or currency values.",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ishares_controlled_parser_probe_{run_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"ISHARES_CONTROLLED_PARSER_PROBE_OK | artifact={path} | rows={len(rows)}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure-probe", required=True)
    parser.add_argument("--output-dir", default="output/pricing")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    build(Path(args.structure_probe), Path(args.output_dir), args.run_id)


if __name__ == "__main__":
    main()
