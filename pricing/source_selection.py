from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from pricing.price_result_schema import PriceIdentity, PriceResult, STATUS_UNRESOLVED_NOT_CONFIGURED, SourceLineage
from pricing.sources.base import PriceRequest, PriceSource


@dataclass(frozen=True)
class SourceSelection:
    """Config-derived provider ordering for one trading line."""

    source_ids: tuple[str, ...]

    @classmethod
    def from_policy_row(cls, policy_row: dict) -> "SourceSelection":
        return cls(tuple(str(src.get("source_id", "")).strip() for src in policy_row.get("source_order", []) if str(src.get("source_id", "")).strip()))


def select_sources(selection: SourceSelection, available_sources: dict[str, PriceSource]) -> list[PriceSource]:
    """Return configured providers in policy order, ignoring sources not implemented in this branch."""

    return [available_sources[source_id] for source_id in selection.source_ids if source_id in available_sources]


def first_resolved_or_last_unresolved(identity: PriceIdentity, sources: Iterable[PriceSource], *, requested_date: str | None = None) -> PriceResult:
    """Try providers in order and return the first resolved row, else the last typed unresolved row."""

    last_unresolved: PriceResult | None = None
    tried = False
    for source in sources:
        tried = True
        result = source.fetch_eod_close(PriceRequest(identity=identity, requested_date=requested_date))
        if result.is_resolved:
            return result
        last_unresolved = result
    if last_unresolved is not None:
        return last_unresolved
    return PriceResult.unresolved(
        identity=identity,
        lineage=SourceLineage.now(
            source_id="none",
            provider_name="none",
            license_class="unknown",
            authority_tier="unknown",
        ),
        status=STATUS_UNRESOLVED_NOT_CONFIGURED,
        errors=["no_configured_price_source_available" if tried else "no_price_sources_supplied"],
    )
