from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.boerse-frankfurt.de",
    "Referer": "https://www.boerse-frankfurt.de/",
}


def _get(url: str, params: dict[str, str] | None = None) -> dict[str, object]:
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=20, allow_redirects=True)
        text = response.text
        return {
            "requested_url": url,
            "final_url": response.url,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "content_length": len(response.content),
            "sha256": hashlib.sha256(response.content).hexdigest(),
            "prefix": text[:5000],
        }
    except Exception as exc:
        return {"requested_url": url, "error": type(exc).__name__, "message": str(exc)[:500]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp())
    end = int(datetime(2026, 7, 27, tzinfo=timezone.utc).timestamp())
    tv_url = "https://api.boerse-frankfurt.de/v1/tradingview/lightweight/history/single"
    quote_parameters_url = "https://www.cashmarket.deutsche-boerse.com/resource/blob/1502614/5dad7acb05b04671f3267b74e1182f45/data/QuoteParameters.csv"
    probes = [
        {
            "source": "xetra_quote_parameters_csv",
            **_get(quote_parameters_url),
        },
        {
            "source": "boerse_frankfurt_tradingview_no_resolution",
            **_get(tv_url, {"from": str(start), "to": str(end), "symbols": "XETR:IE00BMC38736"}),
        },
        {
            "source": "boerse_frankfurt_tradingview_resolution_d",
            **_get(tv_url, {"from": str(start), "to": str(end), "symbols": "XETR:IE00BMC38736", "resolution": "D"}),
        },
        {
            "source": "boerse_frankfurt_tradingview_resolution_1d",
            **_get(tv_url, {"from": str(start), "to": str(end), "symbols": "XETR:IE00BMC38736", "resolution": "1D"}),
        },
        {
            "source": "boerse_frankfurt_price_history_html",
            **_get("https://www.boerse-frankfurt.de/en/etf/vaneck-semiconductor-ucits-etf-usd-acc/price-history/historical-prices-and-volumes"),
        },
    ]
    payload = {
        "schema_version": "official_xetra_source_probe_v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "portfolio_mutation": False,
        "probes": probes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
