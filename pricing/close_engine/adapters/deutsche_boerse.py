from __future__ import annotations

import html
import re
import urllib.request
from dataclasses import dataclass
from typing import Any

from pricing.close_engine.contracts import CloseObservation, SourcePolicy, TradingLine

NUMBER_RE = re.compile(r"\b[0-9]{1,5}(?:[.,][0-9]{1,6})?\b")
DATE_RE = re.compile(r"\b(?:20[0-9]{2}-[01][0-9]-[0-3][0-9]|[0-3]?[0-9][./-][01]?[0-9][./-]20[0-9]{2})\b")
QUOTED_STRING_RE = re.compile(r"[\"']([^\"']{2,400})[\"']")
SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script>", flags=re.IGNORECASE | re.DOTALL)
QUOTE_KEY_HINTS = [
    "lastPrice",
    "last_price",
    "lastValue",
    "previousClose",
    "closingPrice",
    "closePrice",
    "close",
    "currency",
    "isin",
    "wkn",
    "mic",
    "securityId",
    "instrumentId",
    "quote",
]


@dataclass(frozen=True)
class ParseResult:
    candidate_close: float | None
    candidate_date: str | None
    parser_status: str
    confidence: str
    blockers: list[str]
    diagnostics: dict[str, Any]


class DeutscheBoerseAdapter:
    adapter_name = "deutsche_boerse_live"

    def supports(self, source: SourcePolicy, line: TradingLine) -> bool:
        return source.source_id == "deutsche_boerse_live"

    def observe(self, source: SourcePolicy, line: TradingLine) -> CloseObservation:
        base_blockers = [
            "candidate_observation_only",
            "valuation_grade_promotion_not_allowed_in_adapter",
            "completed_session_not_verified",
        ]
        fetch_result = self._fetch_page(source.source_url)
        if fetch_result.get("error"):
            blockers = base_blockers + ["source_page_fetch_failed", "candidate_close_not_parsed", "candidate_date_not_verified"]
            return self._observation(
                line=line,
                source=source,
                observation_status="source_page_fetch_failed",
                candidate_close=None,
                candidate_date=None,
                confidence="none",
                parser_status="fetch_failed",
                blockers=blockers,
                diagnostics={"fetch_error": fetch_result.get("error"), "http_status": fetch_result.get("http_status")},
            )

        parsed = self._parse_page(fetch_result.get("text") or "")
        blockers = base_blockers + parsed.blockers
        return self._observation(
            line=line,
            source=source,
            observation_status="candidate_close_observed_unverified" if parsed.candidate_close is not None else "candidate_close_not_observed",
            candidate_close=parsed.candidate_close,
            candidate_date=parsed.candidate_date,
            confidence=parsed.confidence,
            parser_status=parsed.parser_status,
            blockers=blockers,
            diagnostics={
                "http_status": fetch_result.get("http_status"),
                **parsed.diagnostics,
            },
        )

    def _observation(
        self,
        line: TradingLine,
        source: SourcePolicy,
        observation_status: str,
        candidate_close: float | None,
        candidate_date: str | None,
        confidence: str,
        parser_status: str,
        blockers: list[str],
        diagnostics: dict[str, Any],
    ) -> CloseObservation:
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
            observation_status=observation_status,
            candidate_close=candidate_close,
            candidate_date=candidate_date,
            candidate_currency=source.expected_currency if candidate_close is not None else None,
            completed_session=False,
            confidence=confidence,
            parser_status=parser_status,
            blockers=blockers,
            source_lineage={
                "authority": source.authority,
                "mic_code": source.mic_code,
                "expected_currency": source.expected_currency,
                "accept_as_valuation_grade": source.accept_as_valuation_grade,
                "adapter_diagnostics": diagnostics,
            },
        )

    @staticmethod
    def _fetch_page(url: str | None) -> dict[str, Any]:
        if not url:
            return {"http_status": None, "text": "", "error": "missing_source_url"}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as response:
                text = response.read().decode("utf-8", errors="replace")
                return {"http_status": getattr(response, "status", None), "text": text, "error": None}
        except Exception as exc:  # pragma: no cover - remote provider dependent
            return {"http_status": None, "text": "", "error": str(exc)}

    @staticmethod
    def _clean_text(raw: str) -> str:
        cleaned = re.sub(r"<script.*?</script>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<style.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = html.unescape(cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()

    def _parse_page(self, raw: str) -> ParseResult:
        text = self._clean_text(raw)
        close_window = self._window_after_label(text, "Schlusspreis des letzten Handelstages", 360)
        last_price_window = self._window_after_label(text, "Letzter Preis", 260)
        currency_window = self._window_after_label(text, "Handelswährung", 120)

        close_audit = self._numeric_candidate_audit(close_window)
        last_price_audit = self._numeric_candidate_audit(last_price_window)
        close_candidates = self._accepted_values(close_audit)
        last_price_candidates = self._accepted_values(last_price_audit)
        date_candidates = DATE_RE.findall(close_window + " " + last_price_window)

        candidate_close = close_candidates[0] if close_candidates else None
        candidate_date = date_candidates[0] if date_candidates else None
        blockers: list[str] = []
        if candidate_close is None:
            blockers.append("candidate_close_not_parsed")
        else:
            blockers.append("candidate_close_unverified")
        if candidate_date is None:
            blockers.append("candidate_date_not_verified")
        else:
            blockers.append("candidate_date_unverified")
        blockers.append("official_completed_session_not_verified")

        parser_status = "candidate_close_parsed_unverified" if candidate_close is not None else "no_clean_close_candidate_found"
        confidence = "low" if candidate_close is not None else "none"
        script_diagnostics = self._script_diagnostics(raw)
        return ParseResult(
            candidate_close=candidate_close,
            candidate_date=candidate_date,
            parser_status=parser_status,
            confidence=confidence,
            blockers=blockers,
            diagnostics={
                "close_label_present": bool(close_window),
                "last_price_label_present": bool(last_price_window),
                "currency_label_present": bool(currency_window),
                "close_label_window": close_window[:500] if close_window else None,
                "last_price_window": last_price_window[:350] if last_price_window else None,
                "currency_window": currency_window[:180] if currency_window else None,
                "close_numeric_candidates": close_candidates[:10],
                "last_price_numeric_candidates": last_price_candidates[:10],
                "close_numeric_candidate_audit": close_audit[:12],
                "last_price_numeric_candidate_audit": last_price_audit[:12],
                "date_candidates": date_candidates[:10],
                "label_offsets": {
                    "close": self._label_offset(text, "Schlusspreis des letzten Handelstages"),
                    "last_price": self._label_offset(text, "Letzter Preis"),
                    "currency": self._label_offset(text, "Handelswährung"),
                },
                **script_diagnostics,
            },
        )

    @staticmethod
    def _window_after_label(text: str, label: str, window: int) -> str:
        idx = text.lower().find(label.lower())
        if idx < 0:
            return ""
        return text[idx: idx + window].strip()

    @staticmethod
    def _label_offset(text: str, label: str) -> int | None:
        idx = text.lower().find(label.lower())
        return idx if idx >= 0 else None

    @staticmethod
    def _accepted_values(audit: list[dict[str, Any]]) -> list[float]:
        values: list[float] = []
        for item in audit:
            value = item.get("value")
            if item.get("accepted") is True and isinstance(value, (int, float)) and value not in values:
                values.append(float(value))
        return values

    def _numeric_candidate_audit(self, text: str) -> list[dict[str, Any]]:
        audit: list[dict[str, Any]] = []
        seen_accepted: set[float] = set()
        for match in NUMBER_RE.finditer(text):
            token = match.group(0)
            value = self._parse_number(token)
            context = self._context(text, match.start(), match.end())
            rejection_reasons: list[str] = []
            if value <= 100 or value > 2000:
                rejection_reasons.append("outside_bootstrap_price_range")
            context_reason = self._non_price_context_reason(text, match.start(), match.end())
            if context_reason:
                rejection_reasons.append(context_reason)
            if not rejection_reasons and value in seen_accepted:
                rejection_reasons.append("duplicate_candidate")
            accepted = not rejection_reasons
            if accepted:
                seen_accepted.add(value)
            audit.append({
                "token": token,
                "value": value,
                "accepted": accepted,
                "rejection_reasons": rejection_reasons,
                "context": context,
            })
        return audit

    @staticmethod
    def _parse_number(token: str) -> float:
        return float(token.replace(".", "").replace(",", ".")) if "," in token else float(token)

    @staticmethod
    def _context(text: str, start: int, end: int, radius: int = 36) -> str:
        return text[max(0, start - radius):min(len(text), end + radius)].strip()

    @staticmethod
    def _non_price_context_reason(text: str, start: int, end: int) -> str | None:
        before = text[max(0, start - 28):start].lower()
        after = text[end:min(len(text), end + 48)].lower()
        around = f"{before}{text[start:end].lower()}{after}"
        if re.search(r"s\s*&\s*p\s*$", before) or re.search(r"s\s*&\s*p\s*\d+\s+ucits", around):
            return "index_name_context"
        if any(term in around for term in ["52-wochen", "52-woche", "handelszeiten", "wkn", "isin"]):
            return "metadata_or_layout_context"
        if re.search(r"\b[0-2]?\d:[0-5]\d\b", around):
            return "time_range_context"
        return None

    @staticmethod
    def _script_diagnostics(raw: str) -> dict[str, Any]:
        script_bodies = SCRIPT_RE.findall(raw)
        script_text = "\n".join(script_bodies)
        key_hits = [key for key in QUOTE_KEY_HINTS if re.search(re.escape(key), script_text, flags=re.IGNORECASE)]
        endpoint_hints: list[str] = []
        for match in QUOTED_STRING_RE.finditer(script_text + "\n" + raw):
            value = html.unescape(match.group(1)).strip()
            lower = value.lower()
            if value.startswith(("data:", "javascript:")):
                continue
            if not any(term in lower for term in ["quote", "price", "instrument", "security", "api", "chart", "history", "xetra"]):
                continue
            if value not in endpoint_hints:
                endpoint_hints.append(value)
            if len(endpoint_hints) >= 40:
                break
        return {
            "script_tag_count": len(script_bodies),
            "script_text_bytes": len(script_text.encode("utf-8", errors="replace")),
            "embedded_quote_key_hits": key_hits[:30],
            "endpoint_hint_samples": endpoint_hints[:20],
            "next_step": "inspect endpoint hints before promoting any candidate close",
        }
