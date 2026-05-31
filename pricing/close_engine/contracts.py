from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class TradingLine:
    registry_id: str
    isin: str
    exchange: str
    exchange_ticker: str
    trading_currency: str
    provider_symbol: str | None = None
    pricing_symbol_yahoo: str | None = None


@dataclass(frozen=True)
class SourcePolicy:
    source_id: str
    adapter_name: str
    authority: str
    valuation_grade_eligible: bool
    accept_as_valuation_grade: bool
    source_url: str | None = None
    mic_code: str | None = None
    expected_currency: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CloseObservation:
    registry_id: str
    isin: str
    exchange: str
    exchange_ticker: str
    trading_currency: str
    provider_symbol: str | None
    source_id: str
    adapter_name: str
    source_url: str | None
    observation_status: str
    candidate_close: float | None
    candidate_date: str | None
    candidate_currency: str | None
    completed_session: bool
    confidence: str
    parser_status: str
    blockers: list[str]
    source_lineage: dict[str, Any]
    portfolio_mutation: bool = False
    production_delivery: bool = False
    funding_authority: bool = False
    valuation_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
