from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
import yaml
from pypdf import PdfReader

BASE_API = "https://api.boerse-frankfurt.de"
SIGNING_SALT = "w4ivc1ATTGta6njAZzMbkL3kJwxMfEAKDa3MNr"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "text/html,application/pdf,application/json,text/plain,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,nl;q=0.8",
}
QUOTE_PARAMETERS_URL = "https://www.cashmarket.deutsche-boerse.com/resource/blob/1502614/5dad7acb05b04671f3267b74e1182f45/data/QuoteParameters.csv"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def signed_headers(url: str) -> dict[str, str]:
    now = datetime.now(timezone.utc)
    client_date = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
    trace = hashlib.md5((client_date + url + SIGNING_SALT).encode("ascii")).hexdigest()
    return {
        **HEADERS,
        "Accept": "application/json,text/plain,*/*",
        "Origin": "https://live.deutsche-boerse.com",
        "Referer": "https://live.deutsche-boerse.com/",
        "client-date": client_date,
        "x-client-traceid": trace,
    }


def fetch(session: requests.Session, url: str, *, headers: dict[str, str] | None = None, timeout: int = 35) -> dict[str, Any]:
    captured = utc_now()
    try:
        response = session.get(url, headers=headers or HEADERS, timeout=timeout, allow_redirects=True)
        return {
            "captured_at_utc": captured,
            "requested_url": url,
            "final_url": response.url,
            "http_status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "content_length": len(response.content),
            "sha256": sha256_bytes(response.content),
            "content": response.content,
        }
    except Exception as exc:
        return {
            "captured_at_utc": captured,
            "requested_url": url,
            "error": type(exc).__name__,
            "message": str(exc)[:1000],
            "content": b"",
        }


def public_result(result: dict[str, Any], prefix: int = 500) -> dict[str, Any]:
    payload = {key: value for key, value in result.items() if key != "content"}
    data = result.get("content") or b""
    if data:
        payload["response_prefix"] = data[:prefix].decode("utf-8", errors="replace")
    return payload


def pdf_text(data: bytes) -> tuple[str, int, str | None]:
    try:
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text, len(reader.pages), None
    except Exception as exc:
        return "", 0, f"{type(exc).__name__}: {exc}"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def validate_kid(data: bytes, candidate: dict[str, Any]) -> dict[str, Any]:
    text, page_count, parse_error = pdf_text(data)
    norm = normalize(text)
    isin = str(candidate["isin"])
    expected_date = str(candidate.get("expected_kid_date") or "")
    date_variants = {expected_date, expected_date.replace("-", "/")}
    try:
        dt = datetime.strptime(expected_date, "%Y-%m-%d")
        dutch_months = {
            1: "januari", 2: "februari", 3: "maart", 4: "april",
            5: "mei", 6: "juni", 7: "juli", 8: "augustus",
            9: "september", 10: "oktober", 11: "november", 12: "december",
        }
        date_variants.update({
            dt.strftime("%d %B %Y"),
            f"{dt.day} {dutch_months[dt.month]} {dt.year}",
            f"{dt.day:02d} {dutch_months[dt.month]} {dt.year}",
            dt.strftime("%d-%m-%Y"),
            dt.strftime("%d/%m/%Y"),
        })
    except ValueError:
        pass
    product_tokens = [token for token in re.findall(r"[A-Za-z0-9]+", str(candidate["fund_name"])) if len(token) > 3]
    product_hits = [token for token in product_tokens if token.casefold() in norm]
    result = {
        "page_count": page_count,
        "parse_error": parse_error,
        "text_sha256": sha256_bytes(text.encode("utf-8")),
        "isin_match": isin.casefold() in norm,
        "product_token_hits": product_hits,
        "product_identity_match": len(product_hits) >= max(2, len(product_tokens) // 2),
        "expected_date": expected_date,
        "expected_date_match": any(value.casefold() in norm for value in date_variants if value),
        "ucits_match": "ucits" in norm,
        "kid_or_priips_match": "key information document" in norm or "essentiële-informatiedocument" in norm or "priips" in norm or "kid" in norm,
    }
    result["pass"] = all((
        page_count > 0,
        result["isin_match"],
        result["product_identity_match"],
        result["expected_date_match"],
        result["ucits_match"],
        result["kid_or_priips_match"],
    ))
    return result


def save_raw(raw_dir: Path, filename: str, result: dict[str, Any]) -> str | None:
    data = result.get("content") or b""
    if not data:
        return None
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / filename
    path.write_bytes(data)
    return str(path)


def parse_quote_parameters(data: bytes, isin: str) -> dict[str, Any]:
    text = data.decode("utf-8", errors="replace")
    lines = [line for line in text.splitlines() if isin in line]
    parsed: list[dict[str, str]] = []
    for line in lines:
        fields = [field.strip() for field in line.split(";")]
        if len(fields) >= 8:
            parsed.append({
                "product_assignment_group": fields[0],
                "short_code": fields[1],
                "name": fields[2],
                "isin": fields[3],
                "maximum_spread": fields[4],
                "spread_type": fields[5],
                "minimum_quantity": fields[6],
                "designated_sponsor_liquidity_class": fields[7],
            })
    return {
        "matching_row_count": len(parsed),
        "rows": parsed,
        "market_maker_parameters_present": bool(parsed),
        "actual_timestamped_quote_present": False,
        "activation_role": "market_structure_reference_not_actual_quote_or_liquidity_measurement",
    }


def probe_api(session: requests.Session, candidate: dict[str, Any], latest_date: str) -> dict[str, Any]:
    isin = str(candidate["isin"])
    mic = str(candidate.get("mic") or "XETR")
    history_params = {
        "limit": "20", "offset": "0", "isin": isin, "mic": mic,
        "minDate": latest_date, "maxDate": latest_date,
        "cleanSplit": "false", "cleanPayout": "false", "cleanSubscriptionRights": "false",
    }
    history_url = BASE_API + "/v1/data/price_history?" + urlencode(history_params)
    quote_url = BASE_API + "/v1/data/price_information?" + urlencode({"isin": isin, "mic": mic})
    session_start = int(datetime.fromisoformat(latest_date).replace(tzinfo=timezone.utc).timestamp())
    tv_url = BASE_API + "/v1/tradingview/lightweight/history/single?" + urlencode({
        "from": str(session_start), "to": str(session_start + 86400),
        "symbols": f"{mic}:{isin}", "resolution": "D",
    })
    probes = []
    for role, url in (("completed_close", history_url), ("timestamped_quote", quote_url), ("history_crosscheck", tv_url)):
        result = fetch(session, url, headers=signed_headers(url), timeout=25)
        probes.append({"role": role, **public_result(result, 1500)})
    return {
        "probes": probes,
        "accepted_completed_close": None,
        "accepted_timestamped_bid_ask_size": None,
        "activation_grade_market_evidence_pass": False,
        "blockers": [
            "accepted_current_xetra_eur_completed_close_not_captured",
            "timestamped_xetra_bid_ask_and_quote_size_not_captured",
        ],
    }


def donor_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {str(row.get("ticker")): row for row in csv.DictReader(handle) if row.get("ticker")}


def donor_assessment(rows: dict[str, dict[str, str]], donor_commit: str, path: Path) -> dict[str, Any]:
    mapping = {"ai_compute_infrastructure": "SMH", "cyber_security": "CIBR"}
    result: list[dict[str, Any]] = []
    for exposure, ticker in mapping.items():
        row = rows.get(ticker) or {}
        action = str(row.get("suggested_action") or "")
        fresh_cash = str(row.get("fresh_cash_test") or "")
        initiate = str(row.get("would_initiate_today") or "")
        fresh_add = action in {"add", "buy", "initiate"} or initiate.casefold() in {"yes", "full"}
        result.append({
            "exposure_id": exposure,
            "donor_ticker": ticker,
            "report_date": row.get("report_date"),
            "weight_pct": row.get("weight_pct"),
            "suggested_action": action,
            "fresh_cash_test": fresh_cash,
            "would_initiate_today": initiate,
            "would_initiate_at_current_weight": row.get("would_initiate_at_current_weight"),
            "total_score": row.get("total_score"),
            "donor_target_present": bool(row),
            "donor_fresh_add_direction": fresh_add,
            "status": "current_hold_or_monitor_not_fresh_add" if row and not fresh_add else ("fresh_add" if fresh_add else "missing"),
        })
    return {
        "donor_repository": "market-predictions/weekly-etf",
        "donor_evidence_commit": donor_commit,
        "scorecard_path": str(path),
        "rows": result,
        "current_report_date": max((str(row.get("report_date") or "") for row in rows.values()), default=""),
        "both_exposures_present": all(row["donor_target_present"] for row in result),
        "any_fresh_add_direction": any(row["donor_fresh_add_direction"] for row in result),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    config = yaml.safe_load(args.sources.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise RuntimeError("Source registry must be a YAML object")
    raw_dir = args.output.parent / f"raw_{args.run_id}"
    session = requests.Session()
    quote_parameters = fetch(session, QUOTE_PARAMETERS_URL)
    quote_parameters_public = public_result(quote_parameters, 250)
    quote_parameters_public["raw_path"] = save_raw(raw_dir, "xetra_quote_parameters.csv", quote_parameters)

    candidates: list[dict[str, Any]] = []
    for candidate in config.get("candidates") or []:
        if not isinstance(candidate, dict):
            continue
        symbol = str(candidate["symbol"])
        product = fetch(session, str(candidate["issuer_product_url"]))
        product_text = (product.get("content") or b"").decode("utf-8", errors="replace")
        product_identity = {
            "source": public_result(product, 500),
            "isin_match": str(candidate["isin"]) in product_text,
            "symbol_match": symbol.casefold() in product_text.casefold(),
            "fund_name_match": all(token.casefold() in product_text.casefold() for token in str(candidate["fund_name"]).split()[:2]),
        }
        product_identity["pass"] = product_identity["source"].get("http_status") == 200 and product_identity["isin_match"] and product_identity["fund_name_match"]

        kid = fetch(session, str(candidate["official_kid_url"]))
        kid_path = save_raw(raw_dir, f"{symbol}_official_kid.pdf", kid)
        kid_validation = validate_kid(kid.get("content") or b"", candidate)
        kid_evidence: dict[str, Any] = {
            "official_issuer_source": public_result(kid, 100),
            "official_issuer_raw_path": kid_path,
            "official_issuer_validation": kid_validation,
            "independent_crosscheck": None,
            "pass": kid_validation["pass"] and kid.get("http_status") == 200,
        }
        if candidate.get("regulated_exchange_kid_url"):
            cross = fetch(session, str(candidate["regulated_exchange_kid_url"]))
            cross_path = save_raw(raw_dir, f"{symbol}_regulated_exchange_kid.pdf", cross)
            kid_evidence["independent_crosscheck"] = {
                "source": public_result(cross, 100),
                "raw_path": cross_path,
                "validation": validate_kid(cross.get("content") or b"", candidate),
            }

        ssr = fetch(session, str(candidate["boerse_frankfurt_page_url"]))
        ssr_text = (ssr.get("content") or b"").decode("utf-8", errors="replace")
        exchange_identity = {
            "source": public_result(ssr, 300),
            "raw_path": save_raw(raw_dir, f"{symbol}_boerse_frankfurt_ssr.html", ssr),
            "isin_match": str(candidate["isin"]) in ssr_text,
            "symbol_match": symbol.casefold() in ssr_text.casefold(),
            "xetra_or_mic_match": "XETR" in ssr_text or "Xetra" in ssr_text,
            "eur_match": "EUR" in ssr_text,
        }
        exchange_identity["pass"] = all((
            exchange_identity["source"].get("http_status") == 200,
            exchange_identity["isin_match"], exchange_identity["symbol_match"],
            exchange_identity["xetra_or_mic_match"], exchange_identity["eur_match"],
        ))

        market = probe_api(session, candidate, str(config["latest_completed_session_date"]))
        quote_reference = parse_quote_parameters(quote_parameters.get("content") or b"", str(candidate["isin"]))
        blockers: list[str] = []
        if not product_identity["pass"] or not exchange_identity["pass"]:
            blockers.append("exact_line_identity_not_pass")
        if not kid_evidence["pass"]:
            blockers.append("exact_current_official_kid_not_pass")
        blockers.extend(market["blockers"])
        blockers.append("accepted_20_session_liquidity_measurement_not_captured")
        candidates.append({
            "exposure_id": candidate["exposure_id"], "symbol": symbol, "isin": candidate["isin"],
            "exchange": candidate["exchange"], "mic": candidate["mic"], "currency": candidate["currency"],
            "identity": {"issuer_product": product_identity, "official_exchange": exchange_identity, "pass": product_identity["pass"] and exchange_identity["pass"]},
            "kid": kid_evidence,
            "market_evidence": market,
            "quote_parameter_reference": quote_reference,
            "liquidity": {"accepted_20_session_traded_value_present": False, "pass": False, "blocker": "accepted_20_session_liquidity_measurement_not_captured"},
            "activation_evidence_pass": not blockers,
            "blockers": blockers,
        })

    donor = donor_assessment(donor_rows(args.donor_scorecard), args.donor_commit, args.donor_scorecard)
    payload = {
        "schema_version": "etf_eu_wp09_fresh_product_evidence_v1",
        "artifact_type": "etf_eu_wp09_fresh_product_evidence",
        "run_id": args.run_id,
        "generated_at_utc": utc_now(),
        "report_date": config.get("report_date"),
        "latest_completed_session_date": config.get("latest_completed_session_date"),
        "capture_attempted": True,
        "fresh_network_capture": True,
        "cached_connectivity_promoted": False,
        "source_registry": str(args.sources),
        "source_policy": config.get("source_policy"),
        "external_reference_evidence": config.get("external_reference_evidence"),
        "xetra_quote_parameter_reference": quote_parameters_public,
        "donor_reunderwriting": donor,
        "candidates": candidates,
        "summary": {
            "candidate_count": len(candidates),
            "identity_pass_count": sum(1 for row in candidates if row["identity"]["pass"]),
            "kid_pass_count": sum(1 for row in candidates if row["kid"]["pass"]),
            "accepted_close_pass_count": sum(1 for row in candidates if row["market_evidence"]["accepted_completed_close"] is not None),
            "timestamped_quote_pass_count": sum(1 for row in candidates if row["market_evidence"]["accepted_timestamped_bid_ask_size"] is not None),
            "liquidity_pass_count": sum(1 for row in candidates if row["liquidity"]["pass"]),
            "activation_evidence_pass_count": sum(1 for row in candidates if row["activation_evidence_pass"]),
        },
        "protected_state": {
            "portfolio_path": str(args.portfolio), "portfolio_sha256": sha256_file(args.portfolio),
            "ledger_path": str(args.ledger), "ledger_sha256": sha256_file(args.ledger),
            "portfolio_mutation": False, "ledger_write": False,
        },
        "authority": {"funding_authority": False, "execution_authority": False, "activation_authority": False, "production_delivery_authority": False},
        "executable_trade_intents": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--donor-scorecard", type=Path, required=True)
    parser.add_argument("--donor-commit", required=True)
    parser.add_argument("--portfolio", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args)
    print(json.dumps(payload["summary"], sort_keys=True))
    print(args.output)


if __name__ == "__main__":
    main()
