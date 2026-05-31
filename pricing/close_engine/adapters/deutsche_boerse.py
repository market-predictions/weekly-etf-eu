from __future__ import annotations

from pricing.close_engine.contracts import CloseObservation, SourcePolicy, TradingLine


class DeutscheBoerseAdapter:
    adapter_name = "deutsche_boerse_live"

    def supports(self, source: SourcePolicy, line: TradingLine) -> bool:
        return source.source_id == "deutsche_boerse_live"

    def observe(self, source: SourcePolicy, line: TradingLine) -> CloseObservation:
        blockers = [
            "adapter_scaffold_only",
            "clean_close_label_parser_not_integrated",
            "candidate_close_not_parsed",
            "candidate_date_not_verified",
            "completed_session_not_verified",
        ]
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
            observation_status="adapter_scaffold_pending_parser_integration",
            candidate_close=None,
            candidate_date=None,
            candidate_currency=source.expected_currency,
            completed_session=False,
            confidence="none",
            parser_status="not_integrated",
            blockers=blockers,
            source_lineage={
                "authority": source.authority,
                "mic_code": source.mic_code,
                "expected_currency": source.expected_currency,
                "accept_as_valuation_grade": source.accept_as_valuation_grade,
            },
        )
