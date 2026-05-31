from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from pricing.close_engine.contracts import CloseObservation, SourcePolicy, TradingLine

EURONEXT_HINTS = ["currentPath", "baseUrlSearchQuote", "dynamic_quotes_display", "product_data", "Live quotes"]
QUOTED_STRING_RE = re.compile(r"[\"']([^\"']{2,400})[\"']")


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

        diagnostics = self._diagnose_page(fetch_result.get("text") or "", source)
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

    def _diagnose_page(self, raw: str, source: SourcePolicy) -> DiagnosticResult:
        product_code = str(source.raw.get("product_code") or source.raw.get("provider_symbol") or "")
        present_hints = [hint for hint in EURONEXT_HINTS if hint.lower() in raw.lower()]
        current_path = self._extract_assignment(raw, "currentPath")
        base_url_search_quote = self._extract_assignment(raw, "baseUrlSearchQuote")
        endpoint_hints = self._extract_endpoint_hints(raw, source.source_url)
        diagnostics = {
            "product_code": product_code or None,
            "product_code_present": bool(product_code and product_code.lower() in raw.lower()),
            "endpoint_hints_present": present_hints,
            "current_path_hint": current_path,
            "base_url_search_quote_hint": base_url_search_quote,
            "endpoint_hint_samples": endpoint_hints[:20],
            "script_tag_count": len(re.findall(r"<script\b", raw, flags=re.IGNORECASE)),
            "raw_page_bytes": len(raw.encode("utf-8", errors="replace")),
            "next_step": "integrate stable Euronext quote endpoint before candidate close parsing",
        }
        parser_status = "endpoint_hints_observed" if present_hints or endpoint_hints else "endpoint_hints_not_observed"
        confidence = "low" if parser_status == "endpoint_hints_observed" else "none"
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
            if not any(term in lower for term in ["quote", "quotes", "instrument", "product", "ajax", "api", "search"]):
                continue
            normalized = urllib.parse.urljoin(source_url or "", value) if value.startswith("/") else value
            if normalized not in hints:
                hints.append(normalized)
            if len(hints) >= 40:
                break
        return hints
