from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests


BASE_URL = "https://api.boerse-frankfurt.de"
SALT = "w4ivc1ATTGta6njAZzMbkL3kJwxMfEAKDa3MNr"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.boerse-frankfurt.de",
    "Referer": "https://www.boerse-frankfurt.de/",
}


def _client_headers(url: str) -> dict[str, str]:
    now = datetime.now(timezone.utc)
    client_date = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
    trace = hashlib.md5((client_date + url + SALT).encode("ascii")).hexdigest()
    return {**HEADERS, "client-date": client_date, "x-client-traceid": trace}


def _probe(isin: str) -> dict[str, object]:
    params = {
        "limit": "200",
        "offset": "0",
        "isin": isin,
        "mic": "XETR",
        "minDate": "2026-01-01",
        "maxDate": "2026-07-27",
        "cleanSplit": "false",
        "cleanPayout": "false",
        "cleanSubscriptionRights": "false",
    }
    path = "/v1/data/price_history?" + urlencode(params)
    url = BASE_URL + path
    try:
        response = requests.get(url, headers=_client_headers(url), timeout=20)
        return {
            "isin": isin,
            "url": url,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "response_length": len(response.text),
            "response_prefix": response.text[:5000],
        }
    except Exception as exc:
        return {"isin": isin, "url": url, "error": type(exc).__name__, "message": str(exc)[:500]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "schema_version": "boerse_frankfurt_price_history_probe_v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "portfolio_mutation": False,
        "probes": [_probe(isin) for isin in ("IE00BMC38736", "IE00BG0J4C88", "IE00BKY4W127")],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
