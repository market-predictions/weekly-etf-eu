from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

DEFAULT_SOURCE_POLICY = Path("config/ucits_pricing_source_policy.yml")
DEFAULT_OUTPUT_DIR = Path("output/pricing")
OFFICIAL_SOURCE_IDS = {"euronext_live", "deutsche_boerse_live"}
OBSERVATION_TERMS = ["EUR", "USD", "last", "price", "close", "koers", "slot", "cours", "preis"]
NUMBER_RE = re.compile(r"\b[0-9]{1,5}(?:[.,][0-9]{1,6})?\b")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def fetch_text(url: str, timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
            return {"http_status": getattr(response, "status", None), "error": None, "text": text}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        return {"http_status": exc.code, "error": str(exc), "text": text}
    except Exception as exc:
        return {"http_status": None, "error": str(exc), "text": ""}


def clean_page_text(page_text: str) -> str:
    cleaned = re.sub(r"<script.*?</script>", " ", page_text, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<style.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = cleaned.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", cleaned).strip()


def candidate_observation_text(page_text: str) -> list[str]:
    cleaned = clean_page_text(page_text)
    lowered = cleaned.lower()
    snippets: list[str] = []
    for term in OBSERVATION_TERMS:
        start = 0
        while len(snippets) < 20:
            idx = lowered.find(term.lower(), start)
            if idx < 0:
                break
            snippet = cleaned[max(0, idx - 90): min(len(cleaned), idx + 180)].strip()
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            start = idx + len(term)
    return snippets


def label_window(cleaned_text: str, label: str, window: int = 260) -> dict[str, Any]:
    idx = cleaned_text.lower().find(label.lower())
    if idx < 0:
        return {"label": label, "present": False, "text_window": None, "numeric_candidates": []}
    text_window = cleaned_text[idx:min(len(cleaned_text), idx + window)].strip()
    return {
        "label": label,
        "present": True,
        "text_window": text_window,
        "numeric_candidates": NUMBER_RE.findall(text_window)[:10],
    }


def structured_candidate_observation(source_id: str, page_text: str, source: dict[str, Any]) -> dict[str, Any]:
    cleaned = clean_page_text(page_text)
    if source_id == "euronext_live":
        hints = ["currentPath", "baseUrlSearchQuote", "dynamic_quotes_display", "product_data", "Live quotes"]
        present_hints = [hint for hint in hints if hint.lower() in page_text.lower()]
        product_code = str(source.get("product_code") or "")
        return {
            "source_id": source_id,
            "structured_observation_authority": False,
            "status": "endpoint_hints_observed" if present_hints else "endpoint_hints_not_observed",
            "product_code": product_code,
            "product_code_present": bool(product_code and product_code.lower() in page_text.lower()),
            "endpoint_hints_present": present_hints,
            "candidate_close": None,
            "candidate_date": None,
            "candidate_currency": None,
            "next_step": "identify_stable_euronext_quote_endpoint_before_price_parsing",
        }
    if source_id == "deutsche_boerse_live":
        close = label_window(cleaned, "Schlusspreis des letzten Handelstages")
        currency = label_window(cleaned, "Handelswährung")
        last_price = label_window(cleaned, "Letzter Preis")
        status = "close_label_observed_unparsed" if close.get("present") else "close_label_not_observed"
        return {
            "source_id": source_id,
            "structured_observation_authority": False,
            "status": status,
            "close_label": close,
            "currency_label": currency,
            "last_price_label": last_price,
            "candidate_close": None,
            "candidate_date": None,
            "candidate_currency": source.get("expected_currency") if currency.get("present") else None,
            "next_step": "extract_clean_value_adjacent_to_close_label_and_validate_date_currency_session",
        }
    return {
        "source_id": source_id,
        "structured_observation_authority": False,
        "status": "unsupported_source_id",
        "candidate_close": None,
        "candidate_date": None,
        "candidate_currency": None,
    }


def build_rows(policy: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in policy.get("trading_line_policies") or []:
        for source in line.get("source_order") or []:
            source_id = source.get("source_id")
            if source_id not in OFFICIAL_SOURCE_IDS:
                continue
            if source.get("valuation_grade_eligible") is not True:
                continue
            product_url = source.get("product_url")
            expected_currency = source.get("expected_currency")
            if not product_url or not expected_currency:
                continue
            fetched = fetch_text(str(product_url))
            page_text = fetched.get("text") or ""
            candidate_text = candidate_observation_text(page_text)
            structured = structured_candidate_observation(str(source_id), page_text, source)
            expected_tokens = source.get("expected_tokens") or []
            token_checks = []
            for token in expected_tokens:
                token_text = str(token)
                token_checks.append({"token": token_text, "present": token_text.lower() in page_text.lower()})
            rows.append({
                "registry_id": line.get("registry_id"),
                "isin": line.get("isin"),
                "exchange": line.get("exchange"),
                "exchange_ticker": line.get("exchange_ticker"),
                "trading_currency": line.get("trading_currency"),
                "provider_symbol": line.get("provider_symbol"),
                "source_id": source_id,
                "authority": source.get("authority"),
                "product_url": product_url,
                "mic_code": source.get("mic_code"),
                "expected_currency": expected_currency,
                "http_status": fetched.get("http_status"),
                "fetch_error": fetched.get("error"),
                "expected_token_checks": token_checks,
                "candidate_price_date_currency_text": candidate_text,
                "candidate_observation_status": "candidate_text_observed" if candidate_text else "no_candidate_text_observed",
                "structured_candidate_observation": structured,
                "evidence_status": "official_page_reachable" if fetched.get("http_status") == 200 else "official_page_unresolved",
                "price_extraction": False,
                "portfolio_mutation": False,
                "production_delivery": False,
                "funding_authority": False,
                "valuation_authority": False,
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-policy", default=str(DEFAULT_SOURCE_POLICY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    policy_path = Path(args.source_policy)
    output_dir = Path(args.output_dir)
    run_id = args.run_id or make_run_id()
    rows = build_rows(load_yaml(policy_path))
    artifact = {
        "schema_version": "ucits_official_exchange_page_evidence_v1",
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_policy": str(policy_path),
        "portfolio_mutation": False,
        "production_delivery": False,
        "funding_authority": False,
        "valuation_authority": False,
        "rows": rows,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"ucits_official_exchange_page_evidence_{run_id}.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    observed = sum(1 for row in rows if row.get("candidate_observation_status") == "candidate_text_observed")
    structured = sum(1 for row in rows if (row.get("structured_candidate_observation") or {}).get("status") not in {None, "unsupported_source_id"})
    print(f"UCITS_OFFICIAL_EXCHANGE_PAGE_EVIDENCE_OK | artifact={path} | rows={len(rows)} | candidate_observed={observed} | structured_observed={structured}")


if __name__ == "__main__":
    main()
