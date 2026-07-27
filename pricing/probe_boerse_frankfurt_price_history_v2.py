from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import requests


BASE_URL = "https://api.boerse-frankfurt.de"
SALT = "w4ivc1ATTGta6njAZzMbkL3kJwxMfEAKDa3MNr"


def _now() -> tuple[datetime, str]:
    value = datetime.now(timezone.utc)
    return value, value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _headers(url: str, signature_url: str, include_security: bool) -> dict[str, str]:
    now, client_date = _now()
    trace = hashlib.md5((client_date + signature_url + SALT).encode("utf-8")).hexdigest()
    headers = {
        "Host": "api.boerse-frankfurt.de",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json; charset=utf-8",
        "Origin": "https://www.boerse-frankfurt.de",
        "Referer": "https://www.boerse-frankfurt.de/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
        "Client-Date": client_date,
        "X-Client-TraceId": trace,
    }
    if include_security:
        headers["X-Security"] = hashlib.md5(now.strftime("%Y%m%d%H%M").encode("utf-8")).hexdigest()
    return headers


def _attempt(session: requests.Session, url: str, signature_url: str, include_security: bool, do_options: bool) -> dict[str, object]:
    headers = _headers(url, signature_url, include_security)
    result: dict[str, object] = {
        "signature_scope": "full_url" if signature_url == url else "base_endpoint",
        "include_security": include_security,
        "options_first": do_options,
    }
    try:
        if do_options:
            preflight = session.options(url, headers=headers, timeout=15)
            result["options_status"] = preflight.status_code
            result["options_prefix"] = preflight.text[:500]
        response = session.get(url, headers=headers, timeout=20)
        result.update({
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "response_length": len(response.text),
            "response_prefix": response.text[:5000],
        })
    except Exception as exc:
        result.update({"error": type(exc).__name__, "message": str(exc)[:500]})
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    params = {
        "limit": "200",
        "offset": "0",
        "isin": "IE00BMC38736",
        "mic": "XETR",
        "minDate": "2026-01-01",
        "maxDate": "2026-07-27",
        "cleanSplit": "false",
        "cleanPayout": "false",
        "cleanSubscriptionRights": "false",
    }
    endpoint = BASE_URL + "/v1/data/price_history"
    url = endpoint + "?" + urlencode(params)
    session = requests.Session()
    variants = []
    for signature_url in (url, endpoint):
        for include_security in (False, True):
            for do_options in (False, True):
                variants.append(_attempt(session, url, signature_url, include_security, do_options))
    payload = {
        "schema_version": "boerse_frankfurt_price_history_probe_v2",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "url": url,
        "portfolio_mutation": False,
        "variants": variants,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
