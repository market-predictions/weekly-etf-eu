from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for Twelve Data UCITS symbol discovery") from exc

DEFAULT_SOURCE_POLICY = Path("config/ucits_pricing_source_policy.yml")
DEFAULT_OUTPUT_DIR = Path("output/pricing")
TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _api_key() -> str | None:
    return os.environ.get("TWELVE_DATA_API_KEY") or os.environ.get("TWELVEDATA_API_KEY")


def _query(params: dict[str, Any]) -> str:
    return urllib.parse.urlencode({k: v for k, v in params.items() if v is not None and v != ""})


def _json_request(endpoint: str, params: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    url = f"{TWELVE_DATA_BASE_URL}/{endpoint}?" + _query(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - controlled provider URL
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "http_status": getattr(resp, "status", None),
                "body": json.loads(body) if body else {},
                "body_preview": body[:300],
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        parsed: Any
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = None
        return {
            "http_status": exc.code,
            "body": parsed,
            "body_preview": body[:300],
            "error": str(exc),
        }
    except Exception as exc:  # pragma: no cover - remote provider
        return {
            "http_status": None,
            "body": None,
            "body_preview": None,
            "error": str(exc),
        }


def _time_series_probe(api_key: str, symbol: str, exchange: str | None, interval: str = "1day", outputsize: int = 5) -> dict[str, Any]:
    response = _json_request("time_series", {
        "symbol": symbol,
        "exchange": exchange,
        "interval": interval,
        "outputsize": outputsize,
        "format": "JSON",
        "apikey": api_key,
    })
    body = response.get("body") if isinstance(response.get("body"), dict) else {}
    values = body.get("values") if isinstance(body, dict) else None
    meta = body.get("meta") if isinstance(body, dict) else None
    ok = isinstance(values, list) and len(values) > 0
    return {
        "endpoint": "time_series",
        "symbol": symbol,
        "exchange": exchange,
        "http_status": response.get("http_status"),
        "status": "candidate_time_series_resolved" if ok else "candidate_time_series_unresolved",
        "provider_status": body.get("status") if isinstance(body, dict) else None,
        "provider_code": body.get("code") if isinstance(body, dict) else None,
        "provider_message": body.get("message") if isinstance(body, dict) else response.get("error"),
        "values_count": len(values) if isinstance(values, list) else 0,
        "latest_datetime": str(values[0].get("datetime"))[:10] if ok and isinstance(values[0], dict) else None,
        "latest_close": values[0].get("close") if ok and isinstance(values[0], dict) else None,
        "meta": meta if isinstance(meta, dict) else None,
        "body_preview": response.get("body_preview"),
    }


def _symbol_search_probe(api_key: str, symbol: str, exchange: str | None = None) -> dict[str, Any]:
    response = _json_request("symbol_search", {
        "symbol": symbol,
        "exchange": exchange,
        "outputsize": 10,
        "format": "JSON",
        "apikey": api_key,
    })
    body = response.get("body") if isinstance(response.get("body"), dict) else {}
    data = body.get("data") if isinstance(body, dict) else None
    ok = isinstance(data, list) and len(data) > 0
    matches: list[dict[str, Any]] = []
    if ok:
        for match in data[:10]:
            if isinstance(match, dict):
                matches.append({
                    "symbol": match.get("symbol"),
                    "instrument_name": match.get("instrument_name"),
                    "exchange": match.get("exchange"),
                    "mic_code": match.get("mic_code"),
                    "currency": match.get("currency"),
                    "country": match.get("country"),
                    "type": match.get("type"),
                })
    return {
        "endpoint": "symbol_search",
        "symbol": symbol,
        "exchange": exchange,
        "http_status": response.get("http_status"),
        "status": "candidate_symbol_matches_found" if ok else "candidate_symbol_matches_not_found",
        "provider_status": body.get("status") if isinstance(body, dict) else None,
        "provider_code": body.get("code") if isinstance(body, dict) else None,
        "provider_message": body.get("message") if isinstance(body, dict) else response.get("error"),
        "matches_count": len(matches),
        "matches": matches,
        "body_preview": response.get("body_preview"),
    }


def _iter_twelve_data_sources(policy: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in policy.get("trading_line_policies") or []:
        line_context = {
            "registry_id": line.get("registry_id"),
            "isin": line.get("isin"),
            "exchange": line.get("exchange"),
            "exchange_ticker": line.get("exchange_ticker"),
            "trading_currency": line.get("trading_currency"),
            "provider_symbol": line.get("provider_symbol"),
        }
        for source in line.get("source_order") or []:
            if source.get("source_id") == "twelve_data":
                result.append({"line": line_context, "source": source})
    return result


def discover(policy_path: Path, output_dir: Path, run_id: str) -> Path:
    policy = _load_yaml(policy_path)
    api_key = _api_key()
    rows: list[dict[str, Any]] = []

    for item in _iter_twelve_data_sources(policy):
        line = item["line"]
        source = item["source"]
        probes = source.get("candidate_symbol_queries") or [{
            "symbol": source.get("symbol"),
            "exchange": source.get("exchange"),
            "note": "primary_source_policy",
        }]
        attempts: list[dict[str, Any]] = []
        if not api_key:
            attempts.append({
                "status": "unresolved_dependency_missing",
                "error": "Missing TWELVE_DATA_API_KEY or TWELVEDATA_API_KEY",
            })
        else:
            for probe in probes:
                symbol = _as_str(probe.get("symbol"))
                exchange = probe.get("exchange")
                exchange = _as_str(exchange) or None
                if not symbol:
                    continue
                attempts.append({
                    "probe_note": probe.get("note"),
                    "time_series": _time_series_probe(
                        api_key=api_key,
                        symbol=symbol,
                        exchange=exchange,
                        interval=source.get("interval") or "1day",
                        outputsize=int(source.get("outputsize") or 5),
                    ),
                    "symbol_search": _symbol_search_probe(api_key=api_key, symbol=symbol, exchange=exchange),
                })
        rows.append({
            **line,
            "source_id": "twelve_data",
            "authority": "candidate_valuation_source",
            "accept_as_valuation_grade": False,
            "expected_currency": source.get("expected_currency"),
            "policy_symbol": source.get("symbol"),
            "policy_exchange": source.get("exchange"),
            "attempts": attempts,
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "schema_version": "ucits_twelve_data_symbol_discovery_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_policy": str(policy_path),
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "valuation_authority": False,
        "rows": rows,
    }
    path = output_dir / f"ucits_twelve_data_symbol_discovery_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    resolved = 0
    for row in rows:
        for attempt in row.get("attempts") or []:
            if (attempt.get("time_series") or {}).get("status") == "candidate_time_series_resolved":
                resolved += 1
    print(
        "UCITS_TWELVE_DATA_SYMBOL_DISCOVERY_OK"
        f" | artifact={path}"
        f" | rows={len(rows)}"
        f" | resolved_time_series_attempts={resolved}"
        " | portfolio_mutation=false | delivery=false"
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    discover(Path(args.source_policy), Path(args.output_dir), args.run_id or _run_id())


if __name__ == "__main__":
    main()
