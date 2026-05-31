from __future__ import annotations

import html
import re
import urllib.request
from dataclasses import dataclass
from typing import Any

from pricing.close_engine.contracts import CloseObservation, SourcePolicy, TradingLine

NUMBER_RE = re.compile(r"\b[0-9]{1,5}(?:[.,][0-9]{1,6})?\b")
DATE_RE = re.compile(r"\b(?:20[0-9]{2}-[01][0-9]-[0-3][0-9]|[0-3]?[0-9][./-][01]?[0-9][./-]20[0-9]{2})\b")


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

        close_candidates = self._plausible_price_candidates(close_window)
        last_price_candidates = self._plausible_price_candidates(last_price_window)
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
                "date_candidates": date_candidates[:10],
            },
        )

    @staticmethod
    def _window_after_label(text: str, label: str, window: int) -> str:
        idx = text.lower().find(label.lower())
        if idx < 0:
            return ""
        return text[idx: idx + window].strip()

    @staticmethod
    def _plausible_price_candidates(text: str) -> list[float]:
        candidates: list[float] = []
        for token in NUMBER_RE.findall(text):
            value = float(token.replace(".", "").replace(",", ".")) if "," in token else float(token)
            # Guard against 52-week labels, trading hours, zero placeholders and tiny navigation numbers.
            if value <= 100 or value > 2000:
                continue
            if value in candidates:
                continue
            candidates.append(value)
        return candidates
