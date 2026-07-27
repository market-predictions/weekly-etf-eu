from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TARGETS = {
    "VVSM": "https://www.boerse-frankfurt.de/en/etf/vaneck-semiconductor-ucits-etf-usd-acc/price-history/historical-prices-and-volumes",
    "SXR8": "https://www.boerse-frankfurt.de/en/etf/ishares-core-s-p-500-ucits-etf-usd-acc/price-history/historical-prices-and-volumes",
}

PATTERNS = [
    r"price_history",
    r"historical",
    r"timeValuePairs",
    r"IE00BMC38736",
    r"IE00B5BMR087",
    r"VVSM",
    r"SXR8",
    r"TransferState",
    r"ng-state",
    r"application/json",
    r"client-date",
    r"x-client-traceid",
    r"lightweight/history",
    r"priceHistory",
    r"historicPrice",
    r"lastPrice",
    r"previousClose",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _script_blocks(text: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    pattern = re.compile(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.IGNORECASE | re.DOTALL)
    for index, match in enumerate(pattern.finditer(text)):
        attrs = match.group("attrs") or ""
        body = match.group("body") or ""
        type_match = re.search(r'type=["\']([^"\']+)', attrs, re.IGNORECASE)
        src_match = re.search(r'src=["\']([^"\']+)', attrs, re.IGNORECASE)
        result.append({
            "index": index,
            "attrs": attrs[:1000],
            "type": type_match.group(1) if type_match else None,
            "src": src_match.group(1) if src_match else None,
            "body_length": len(body),
            "body_sha256": hashlib.sha256(body.encode("utf-8", errors="replace")).hexdigest(),
            "body_prefix": body[:4000],
        })
    return result


def _findings(text: str) -> dict[str, list[dict[str, Any]]]:
    findings: dict[str, list[dict[str, Any]]] = {}
    for raw in PATTERNS:
        matches: list[dict[str, Any]] = []
        for match in re.finditer(raw, text, re.IGNORECASE):
            start = max(0, match.start() - 300)
            end = min(len(text), match.end() + 500)
            matches.append({
                "offset": match.start(),
                "match": match.group(0),
                "context": text[start:end],
            })
            if len(matches) >= 25:
                break
        findings[raw] = matches
    return findings


def capture(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    records: list[dict[str, Any]] = []
    for ticker, url in TARGETS.items():
        try:
            response = session.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
            text = response.text
            html_path = output_dir / f"{ticker.lower()}_price_history_ssr.html"
            html_path.write_text(text, encoding="utf-8")
            scripts = _script_blocks(text)
            findings = _findings(text)
            analysis = {
                "ticker": ticker,
                "requested_url": url,
                "final_url": response.url,
                "http_status": response.status_code,
                "content_type": response.headers.get("content-type"),
                "content_length": len(response.content),
                "html_sha256": hashlib.sha256(response.content).hexdigest(),
                "html_path": str(html_path),
                "script_count": len(scripts),
                "scripts": scripts,
                "findings": findings,
            }
            analysis_path = output_dir / f"{ticker.lower()}_price_history_ssr_analysis.json"
            analysis_path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            records.append({
                "ticker": ticker,
                "http_status": response.status_code,
                "content_length": len(response.content),
                "script_count": len(scripts),
                "html_path": str(html_path),
                "analysis_path": str(analysis_path),
                "finding_counts": {key: len(value) for key, value in findings.items()},
            })
        except Exception as exc:
            records.append({"ticker": ticker, "url": url, "error": type(exc).__name__, "message": str(exc)[:1000]})
    manifest = {
        "schema_version": "boerse_frankfurt_ssr_capture_v1",
        "generated_at_utc": _utc_now(),
        "portfolio_mutation": False,
        "funding_authority": False,
        "records": records,
    }
    (output_dir / "boerse_frankfurt_ssr_capture_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = capture(args.output_dir)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
