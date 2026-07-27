from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests


PAGE_URL = "https://www.boerse-frankfurt.de/en/etf/vaneck-semiconductor-ucits-etf-usd-acc/price-history/historical-prices-and-volumes"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "text/html,application/javascript,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
TERMS = [
    "price_history",
    "priceHistory",
    "historical-prices",
    "lightweight/history",
    "x-client-traceid",
    "client-date",
    "x-security",
    "X-Security",
    "w4ivc1",
    "md5",
    "traceid",
    "price_history_bid_ask",
    "timeValuePairs",
    "cleanSubscriptionRights",
    "api.boerse-frankfurt.de",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _findings(text: str) -> dict[str, list[dict[str, object]]]:
    result: dict[str, list[dict[str, object]]] = {}
    for term in TERMS:
        matches: list[dict[str, object]] = []
        for match in re.finditer(re.escape(term), text, re.IGNORECASE):
            start = max(0, match.start() - 1000)
            end = min(len(text), match.end() + 2500)
            matches.append({"offset": match.start(), "match": match.group(0), "context": text[start:end]})
            if len(matches) >= 50:
                break
        result[term] = matches
    return result


def capture(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    page = session.get(PAGE_URL, headers=HEADERS, timeout=30, allow_redirects=True)
    page.raise_for_status()
    script_sources = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', page.text, re.IGNORECASE)
    assets: list[dict[str, object]] = []
    for source in script_sources:
        asset_url = urljoin(page.url, source)
        try:
            response = session.get(asset_url, headers=HEADERS, timeout=45)
            content = response.text
            filename = source.rsplit("/", 1)[-1].split("?", 1)[0] or "bundle.js"
            path = output_dir / filename
            path.write_text(content, encoding="utf-8")
            findings = _findings(content)
            analysis_path = output_dir / f"{filename}.analysis.json"
            analysis_path.write_text(json.dumps({
                "source": source,
                "asset_url": asset_url,
                "http_status": response.status_code,
                "content_type": response.headers.get("content-type"),
                "content_length": len(response.content),
                "sha256": hashlib.sha256(response.content).hexdigest(),
                "findings": findings,
            }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            assets.append({
                "source": source,
                "asset_url": asset_url,
                "http_status": response.status_code,
                "content_length": len(response.content),
                "path": str(path),
                "analysis_path": str(analysis_path),
                "finding_counts": {key: len(value) for key, value in findings.items()},
            })
        except Exception as exc:
            assets.append({"source": source, "asset_url": asset_url, "error": type(exc).__name__, "message": str(exc)[:1000]})
    manifest = {
        "schema_version": "boerse_frankfurt_client_bundle_capture_v1",
        "generated_at_utc": _utc_now(),
        "page_final_url": page.url,
        "portfolio_mutation": False,
        "assets": assets,
    }
    (output_dir / "bundle_capture_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(capture(args.output_dir), indent=2))


if __name__ == "__main__":
    main()
