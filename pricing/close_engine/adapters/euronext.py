from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from pricing.close_engine.contracts import CloseObservation, SourcePolicy, TradingLine

EURONEXT_HINTS = ["currentPath", "baseUrlSearchQuote", "dynamic_quotes_display", "product_data", "Live quotes"]
QUOTED_STRING_RE = re.compile(r"[\"']([^\"']{2,700})[\"']")
CANONICAL_HREF_RE = re.compile(r"<link\b[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)[\"']", re.IGNORECASE)
CANONICAL_HREF_RE_REVERSED = re.compile(r"<link\b[^>]*href=[\"']([^\"']+)[\"'][^>]*rel=[\"']canonical[\"']", re.IGNORECASE)
DRUPAL_SETTINGS_RE = re.compile(
    r"<script\b[^>]*data-drupal-selector=[\"']drupal-settings-json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
SIGNAL_TERMS = [
    "dynamic_quotes_display",
    "product_data",
    "baseUrlSearchQuote",
    "currentPath",
    "ajaxPageState",
    "ajaxTrustedUrl",
    "ajax_secure",
    "ewl_related_instruments",
    "nameInstrument",
]
ENDPOINT_TERMS = ["quote", "quotes", "instrument", "product", "ajax", "api", "search", "market", "price", "chart"]


@dataclass(frozen=True)
class DiagnosticResult:
    parser_status: str
    confidence: str
    diagnostics: dict[str, Any]


class EuronextAdapter:
    adapter_name = "euronext_live"

    def supports(self, source: SourcePolicy, line: TradingLine) -> bool:
        return source.source_id == "euronext_live"

    def observe(self, source: SourcePolicy, line: TradingLine) -> CloseObservation:
        base_blockers = [
            "adapter_scaffold_only",
            "stable_euronext_quote_endpoint_not_integrated",
            "candidate_close_not_parsed",
            "candidate_date_not_verified",
            "completed_session_not_verified",
        ]
        fetch_result = self._fetch_page(source.source_url)
        if fetch_result.get("error"):
            return CloseObservation(
                registry_id=line.registry_id,
                isin=line.isin,
                exchange=line.exchange,
                exchange_ticker=line.exchange_ticker,
                trading_currency=line.trading_currency,
                provider_symbol=line.provider_symbol,
                source_id=source.source_id,
                adapter_name=self.adapter_name,
                source_url=source.source_url,
                observation_status="source_page_fetch_failed",
                candidate_close=None,
                candidate_date=None,
                candidate_currency=None,
                completed_session=False,
                confidence="none",
                parser_status="fetch_failed",
                blockers=base_blockers + ["source_page_fetch_failed"],
                source_lineage=self._source_lineage(
                    source,
                    {
                        "fetch_error": fetch_result.get("error"),
                        "http_status": fetch_result.get("http_status"),
                        "final_url": fetch_result.get("final_url"),
                    },
                ),
            )

        diagnostics = self._diagnose_page(fetch_result.get("text") or "", source, line)
        blockers = list(base_blockers)
        if diagnostics.parser_status == "endpoint_hints_not_observed":
            blockers.append("euronext_endpoint_hints_not_observed")

        return CloseObservation(
            registry_id=line.registry_id,
            isin=line.isin,
            exchange=line.exchange,
            exchange_ticker=line.exchange_ticker,
            trading_currency=line.trading_currency,
            provider_symbol=line.provider_symbol,
            source_id=source.source_id,
            adapter_name=self.adapter_name,
            source_url=source.source_url,
            observation_status="adapter_scaffold_pending_endpoint_integration",
            candidate_close=None,
            candidate_date=None,
            candidate_currency=None,
            completed_session=False,
            confidence=diagnostics.confidence,
            parser_status=diagnostics.parser_status,
            blockers=blockers,
            source_lineage=self._source_lineage(
                source,
                {
                    "http_status": fetch_result.get("http_status"),
                    "final_url": fetch_result.get("final_url"),
                    **diagnostics.diagnostics,
                },
            ),
        )

    @staticmethod
    def _source_lineage(source: SourcePolicy, diagnostics: dict[str, Any]) -> dict[str, Any]:
        return {
            "authority": source.authority,
            "mic_code": source.mic_code,
            "expected_currency": source.expected_currency,
            "accept_as_valuation_grade": source.accept_as_valuation_grade,
            "adapter_diagnostics": diagnostics,
        }

    @staticmethod
    def _fetch_page(url: str | None) -> dict[str, Any]:
        if not url:
            return {"http_status": None, "final_url": None, "text": "", "error": "missing_source_url"}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as response:
                text = response.read().decode("utf-8", errors="replace")
                return {
                    "http_status": getattr(response, "status", None),
                    "final_url": getattr(response, "url", None),
                    "text": text,
                    "error": None,
                }
        except Exception as exc:  # pragma: no cover - remote provider dependent
            return {"http_status": None, "final_url": url, "text": "", "error": str(exc)}

    def _diagnose_page(self, raw: str, source: SourcePolicy, line: TradingLine) -> DiagnosticResult:
        product_code = str(source.raw.get("product_code") or source.raw.get("provider_symbol") or "")
        present_hints = [hint for hint in EURONEXT_HINTS if hint.lower() in raw.lower()]
        current_path = self._extract_assignment(raw, "currentPath")
        base_url_search_quote = self._extract_assignment(raw, "baseUrlSearchQuote")
        endpoint_hints = self._extract_endpoint_hints(raw, source.source_url)
        search_probe_results = self._probe_search_endpoints(
            source_url=source.source_url,
            base_url_search_quote=base_url_search_quote,
            product_code=product_code,
            line=line,
        )
        diagnostics = {
            "product_code": product_code or None,
            "product_code_present": bool(product_code and product_code.lower() in raw.lower()),
            "endpoint_hints_present": present_hints,
            "current_path_hint": current_path,
            "base_url_search_quote_hint": base_url_search_quote,
            "endpoint_hint_samples": endpoint_hints[:20],
            "search_endpoint_probe_results": search_probe_results,
            "resolved_product_url_candidates": self._resolved_product_url_candidates(search_probe_results, source.source_url),
            "product_page_signal_diagnostics": self._product_page_signal_diagnostics(raw, source.source_url, line),
            "script_tag_count": len(re.findall(r"<script\b", raw, flags=re.IGNORECASE)),
            "raw_page_bytes": len(raw.encode("utf-8", errors="replace")),
            "next_step": "select a stable Euronext product or quote endpoint from typed product-page diagnostics before any candidate close parsing",
        }
        parser_status = "product_page_signal_diagnostics_collected" if diagnostics["product_page_signal_diagnostics"].get("signal_terms_present") else "endpoint_probe_completed" if search_probe_results else "endpoint_hints_observed" if present_hints or endpoint_hints else "endpoint_hints_not_observed"
        confidence = "low" if parser_status != "endpoint_hints_not_observed" else "none"
        return DiagnosticResult(parser_status=parser_status, confidence=confidence, diagnostics=diagnostics)

    @staticmethod
    def _extract_assignment(raw: str, name: str) -> str | None:
        patterns = [
            rf"{re.escape(name)}\s*[:=]\s*[\"']([^\"']+)[\"']",
            rf"[\"']{re.escape(name)}[\"']\s*:\s*[\"']([^\"']+)[\"']",
        ]
        for pattern in patterns:
            match = re.search(pattern, raw, flags=re.IGNORECASE)
            if match:
                return html.unescape(match.group(1).strip())
        return None

    @staticmethod
    def _extract_endpoint_hints(raw: str, source_url: str | None) -> list[str]:
        hints: list[str] = []
        for match in QUOTED_STRING_RE.finditer(raw):
            value = html.unescape(match.group(1)).strip()
            lower = value.lower()
            if value.startswith(("data:", "javascript:")):
                continue
            if not any(term in lower for term in ENDPOINT_TERMS):
                continue
            normalized = urllib.parse.urljoin(source_url or "", value) if value.startswith("/") else value
            if normalized not in hints:
                hints.append(normalized)
            if len(hints) >= 40:
                break
        return hints

    def _probe_search_endpoints(
        self,
        source_url: str | None,
        base_url_search_quote: str | None,
        product_code: str,
        line: TradingLine,
    ) -> list[dict[str, Any]]:
        if not source_url or not base_url_search_quote:
            return []
        base_path = self._normalize_hint_path(base_url_search_quote)
        query_values = [value for value in [product_code, line.isin, line.exchange_ticker] if value]
        candidate_urls: list[tuple[str, str]] = []
        for value in query_values:
            encoded = urllib.parse.quote(value)
            candidate_urls.extend([
                (f"search_path:{value}", urllib.parse.urljoin(source_url, base_path + encoded)),
                (f"search_query:{value}", urllib.parse.urljoin(source_url, base_path + "?search=" + encoded)),
                (f"search_q:{value}", urllib.parse.urljoin(source_url, base_path + "?q=" + encoded)),
            ])
        results: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        for probe_name, url in candidate_urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            results.append(self._fetch_probe(probe_name, url, line))
            if len(results) >= 9:
                break
        return results

    @staticmethod
    def _normalize_hint_path(value: str) -> str:
        normalized = html.unescape(value).replace("\\/", "/").strip()
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        if not normalized.endswith("/") and "?" not in normalized:
            normalized += "/"
        return normalized

    @classmethod
    def _fetch_probe(cls, probe_name: str, url: str, line: TradingLine) -> dict[str, Any]:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                raw = response.read(6000)
                text = raw.decode("utf-8", errors="replace")
                lowered = text.lower()
                canonical_url = cls._extract_canonical_url(text, url)
                product_links = cls._extract_product_link_candidates(text, url)
                return {
                    "probe_name": probe_name,
                    "url": url,
                    "http_status": getattr(response, "status", None),
                    "content_type": response.headers.get("content-type"),
                    "bytes_sampled": len(raw),
                    "looks_json": text.lstrip().startswith(("{", "[")),
                    "contains_isin": line.isin.lower() in lowered,
                    "contains_exchange_ticker": line.exchange_ticker.lower() in lowered,
                    "contains_trading_currency_token": cls._contains_currency_token(text, line.trading_currency),
                    "contains_close_terms": any(term in lowered for term in ["close", "closing", "last", "price", "currency"]),
                    "canonical_url": canonical_url,
                    "canonical_matches_source_line_pattern": bool(canonical_url and f"/{line.isin}".lower() in canonical_url.lower()),
                    "product_link_candidate_count": len(product_links),
                    "product_link_candidates": product_links[:10],
                    "body_sample": re.sub(r"\s+", " ", text[:700]).strip(),
                }
        except Exception as exc:  # pragma: no cover - remote provider dependent
            return {
                "probe_name": probe_name,
                "url": url,
                "http_status": None,
                "content_type": None,
                "bytes_sampled": 0,
                "error": str(exc),
            }

    @staticmethod
    def _extract_canonical_url(text: str, base_url: str) -> str | None:
        for pattern in [CANONICAL_HREF_RE, CANONICAL_HREF_RE_REVERSED]:
            match = pattern.search(text)
            if match:
                return urllib.parse.urljoin(base_url, html.unescape(match.group(1).strip()))
        return None

    @staticmethod
    def _extract_product_link_candidates(text: str, base_url: str) -> list[str]:
        candidates: list[str] = []
        for match in QUOTED_STRING_RE.finditer(text):
            value = html.unescape(match.group(1)).strip()
            lower = value.lower()
            if "/product/" not in lower or "/etfs/" not in lower:
                continue
            normalized = urllib.parse.urljoin(base_url, value)
            if normalized not in candidates:
                candidates.append(normalized)
            if len(candidates) >= 20:
                break
        return candidates

    @classmethod
    def _product_page_signal_diagnostics(cls, raw: str, source_url: str | None, line: TradingLine) -> dict[str, Any]:
        signal_counts = {term: len(re.findall(re.escape(term), raw, flags=re.IGNORECASE)) for term in SIGNAL_TERMS}
        settings_payload = cls._extract_drupal_settings(raw)
        settings_summary = cls._summarize_drupal_settings(settings_payload, source_url)
        endpoint_candidates = cls._extract_endpoint_hints(raw, source_url)[:30]
        return {
            "signal_terms_present": [term for term, count in signal_counts.items() if count > 0],
            "signal_term_counts": signal_counts,
            "signal_context_samples": cls._signal_context_samples(raw, SIGNAL_TERMS, limit=20),
            "endpoint_candidate_samples": endpoint_candidates,
            "endpoint_candidate_count": len(endpoint_candidates),
            "drupal_settings_present": settings_payload is not None,
            "drupal_settings_summary": settings_summary,
            "product_identity_tokens_present": {
                "isin": line.isin.lower() in raw.lower(),
                "exchange_ticker": line.exchange_ticker.lower() in raw.lower(),
                "currency_token": cls._contains_currency_token(raw, line.trading_currency),
            },
            "diagnostic_only": True,
        }

    @staticmethod
    def _extract_drupal_settings(raw: str) -> dict[str, Any] | None:
        match = DRUPAL_SETTINGS_RE.search(raw)
        if not match:
            return None
        payload = html.unescape(match.group(1)).strip()
        if not payload:
            return None
        try:
            loaded = json.loads(payload)
        except json.JSONDecodeError as exc:
            return {"_parse_error": str(exc), "_raw_sample": payload[:500]}
        return loaded if isinstance(loaded, dict) else {"_non_object_settings_type": type(loaded).__name__}

    @classmethod
    def _summarize_drupal_settings(cls, settings: dict[str, Any] | None, source_url: str | None) -> dict[str, Any]:
        if settings is None:
            return {"parse_status": "settings_not_found"}
        if "_parse_error" in settings:
            return {
                "parse_status": "json_parse_failed",
                "parse_error": settings.get("_parse_error"),
                "raw_sample": settings.get("_raw_sample"),
            }
        endpoint_like_values = cls._walk_endpoint_like_values(settings, source_url)
        signal_key_paths = cls._walk_signal_key_paths(settings)
        return {
            "parse_status": "parsed",
            "top_level_keys": sorted(str(key) for key in settings.keys())[:40],
            "ajax_keys_present": cls._safe_dict_keys(settings.get("ajax")),
            "ajax_page_state_keys_present": cls._safe_dict_keys(settings.get("ajaxPageState")),
            "signal_key_paths": signal_key_paths[:40],
            "endpoint_like_values": endpoint_like_values[:40],
            "endpoint_like_value_count": len(endpoint_like_values),
        }

    @classmethod
    def _walk_endpoint_like_values(cls, value: Any, source_url: str | None, path: str = "$") -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        if isinstance(value, dict):
            for key, child in value.items():
                found.extend(cls._walk_endpoint_like_values(child, source_url, f"{path}.{key}"))
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                found.extend(cls._walk_endpoint_like_values(child, source_url, f"{path}[{idx}]"))
        elif isinstance(value, str):
            lowered = value.lower()
            if any(term in lowered for term in ENDPOINT_TERMS) or value.startswith("/"):
                normalized = urllib.parse.urljoin(source_url or "", html.unescape(value)) if value.startswith("/") else html.unescape(value)
                found.append({"path": path, "value": normalized[:500]})
        return found

    @classmethod
    def _walk_signal_key_paths(cls, value: Any, path: str = "$") -> list[str]:
        found: list[str] = []
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                if any(term.lower() in str(key).lower() for term in [*SIGNAL_TERMS, *ENDPOINT_TERMS]):
                    found.append(child_path)
                found.extend(cls._walk_signal_key_paths(child, child_path))
        elif isinstance(value, list):
            for idx, child in enumerate(value):
                found.extend(cls._walk_signal_key_paths(child, f"{path}[{idx}]"))
        return found

    @staticmethod
    def _safe_dict_keys(value: Any) -> list[str]:
        return sorted(str(key) for key in value.keys())[:40] if isinstance(value, dict) else []

    @staticmethod
    def _signal_context_samples(raw: str, terms: list[str], limit: int) -> list[dict[str, str]]:
        samples: list[dict[str, str]] = []
        for term in terms:
            for match in re.finditer(re.escape(term), raw, flags=re.IGNORECASE):
                samples.append({
                    "term": term,
                    "context": re.sub(r"\s+", " ", raw[max(0, match.start() - 120): match.end() + 180]).strip(),
                })
                if len(samples) >= limit:
                    return samples
        return samples

    @staticmethod
    def _contains_currency_token(text: str, currency: str) -> bool:
        token = currency.strip().lower()
        if not token:
            return False
        return re.search(rf"(?<![a-z]){re.escape(token)}(?![a-z])", text.lower()) is not None

    @staticmethod
    def _resolved_product_url_candidates(probe_results: list[dict[str, Any]], source_url: str | None) -> list[str]:
        candidates: list[str] = []
        for result in probe_results:
            for value in [result.get("canonical_url"), *(result.get("product_link_candidates") or [])]:
                if not value:
                    continue
                normalized = urllib.parse.urljoin(source_url or "", str(value))
                if "/product/" in normalized.lower() and normalized not in candidates:
                    candidates.append(normalized)
        return candidates[:20]
