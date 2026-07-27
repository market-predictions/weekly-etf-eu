from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _signature(text: str) -> dict[str, Any]:
    clean = text[:2000]
    return {
        "length": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest(),
        "prefix": clean,
    }


def _get(session: requests.Session, url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        response = session.get(url, params=params, headers=HEADERS, timeout=12, allow_redirects=True)
        return {
            "requested_url": url,
            "final_url": response.url,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "retry_after": response.headers.get("retry-after"),
            "response": _signature(response.text),
        }
    except Exception as exc:
        return {"requested_url": url, "error": type(exc).__name__, "message": str(exc)[:500]}


def build() -> dict[str, Any]:
    session = requests.Session()
    probes: list[dict[str, Any]] = []
    for symbol in ("VVSM.DE", "PCOM.DE", "IXUA.DE"):
        for host in ("query2.finance.yahoo.com", "query1.finance.yahoo.com"):
            probes.append({
                "source": "yahoo_chart",
                "symbol": symbol,
                **_get(
                    session,
                    f"https://{host}/v8/finance/chart/{quote(symbol, safe='')}",
                    {"range": "6mo", "interval": "1d", "events": "history", "includeAdjustedClose": "true"},
                ),
            })
        probes.append({
            "source": "stooq_csv",
            "symbol": symbol,
            **_get(session, "https://stooq.com/q/d/l/", {"s": symbol.lower(), "i": "d", "d1": "20260101", "d2": "20260727"}),
        })
        probes.append({
            "source": "yahoo_instrument_html",
            "symbol": symbol,
            **_get(session, f"https://finance.yahoo.com/quote/{quote(symbol, safe='')}/history/"),
        })
    return {
        "schema_version": "etf_eu_allocator_source_probe_v1",
        "generated_at_utc": _utc_now(),
        "portfolio_mutation": False,
        "funding_authority": False,
        "probes": probes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
