from __future__ import annotations

import html
import urllib.parse
from typing import Any

CANDIDATE_SCHEMA_VERSION = "euronext_quote_endpoint_candidate_evidence_v1"


def build_quote_endpoint_candidate_evidence(
    settings: dict[str, Any] | None,
    source_url: str | None,
    registry_identity: dict[str, str],
) -> dict[str, Any]:
    """Build diagnostic-only Euronext quote endpoint candidates.

    This helper deliberately does not fetch any endpoint and does not parse prices.
    It only converts the verified Drupal custom.instrument identity into a bounded
    candidate list for a future controlled evidence-fetch patch.
    """
    if not isinstance(settings, dict):
        return {"schema_version": CANDIDATE_SCHEMA_VERSION, "diagnostic_only": True, "reason": "settings_not_available"}
    custom = settings.get("custom") if isinstance(settings.get("custom"), dict) else {}
    instrument = custom.get("instrument") if isinstance(custom.get("instrument"), dict) else {}
    if not instrument:
        return {"schema_version": CANDIDATE_SCHEMA_VERSION, "diagnostic_only": True, "reason": "custom_instrument_not_available"}

    identity = {
        "isin": str(instrument.get("isin") or ""),
        "symbol": str(instrument.get("symbol") or ""),
        "mic": str(instrument.get("mic") or ""),
        "product_data": str(instrument.get("product_data") or ""),
        "url_type": str(instrument.get("url_type") or "etfs"),
    }
    candidate_urls = _candidate_urls(settings=settings, source_url=source_url, identity=identity)
    return {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "diagnostic_only": True,
        "authority": False,
        "candidate_close_extraction": False,
        "completed_session_validation": False,
        "fetch_attempted": False,
        "identity_source": "drupal_settings.custom.instrument",
        "identity": identity,
        "registry_identity": registry_identity,
        "candidate_count": len(candidate_urls),
        "candidate_urls": candidate_urls,
        "next_step": "select one candidate URL for a controlled endpoint evidence fetch before any quote parser exists",
    }


def _candidate_urls(settings: dict[str, Any], source_url: str | None, identity: dict[str, str]) -> list[dict[str, str]]:
    base_url = _settings_base_url(settings=settings, source_url=source_url)
    base_search = str(settings.get("baseUrlSearchQuote") or "/en/search_instruments/").rstrip("/")
    product_data = urllib.parse.quote(identity.get("product_data") or "")
    symbol = urllib.parse.quote(identity.get("symbol") or "")
    isin = urllib.parse.quote(identity.get("isin") or "")
    url_type = urllib.parse.quote(identity.get("url_type") or "etfs")
    raw_candidates = [
        ("product_page_identity", _join_url(base_url, f"/en/product/{url_type}/{product_data}")),
        ("settings_search_product_data", _join_url(base_url, f"{base_search}/{product_data}")),
        ("settings_search_symbol", _join_url(base_url, f"{base_search}/{symbol}")),
        ("settings_search_isin", _join_url(base_url, f"{base_search}/{isin}")),
    ]
    seen: set[str] = set()
    results: list[dict[str, str]] = []
    for name, url in raw_candidates:
        if not url or url in seen or "//" not in url:
            continue
        seen.add(url)
        results.append({"name": name, "url": url})
    return results


def _settings_base_url(settings: dict[str, Any], source_url: str | None) -> str:
    path_settings = settings.get("path") if isinstance(settings.get("path"), dict) else {}
    base = str(path_settings.get("baseUrl") or source_url or "https://live.euronext.com/")
    return urllib.parse.urljoin(source_url or "https://live.euronext.com/", base)


def _join_url(base_url: str, path_or_url: str) -> str:
    value = html.unescape(path_or_url).replace("\\/", "/")
    return urllib.parse.urljoin(base_url, value)
