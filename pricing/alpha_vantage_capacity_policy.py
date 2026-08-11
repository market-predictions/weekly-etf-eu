from __future__ import annotations

from datetime import date

from pricing import ucits_price_provider_engine as engine


_ALLOCATION_CANDIDATE_BASKET_IDS: set[str] = set()


class GovernedAlphaVantageAdapter(engine.AlphaVantageAdapter):
    """Quota-aware Alpha Vantage adapter for the governed ETF EU pricing gate.

    Alpha Vantage remains reserved for authoritative funded positions by default.
    A small set of explicitly declared *allocation candidates* may also consume a
    close request so a new position can obtain two-provider evidence before an
    allocation decision. This breaks the funded-only bootstrap deadlock without
    turning every research line into scarce live-close traffic.

    The exception creates pricing evidence only. It never creates funding,
    portfolio-mutation, delivery or broker-execution authority.
    """

    def bulk_discover(
        self,
        lines: list[engine.InstrumentLine],
        report_date: date,
    ) -> dict[str, engine.ProviderResult]:
        results: dict[str, engine.ProviderResult] = {}
        for line in lines:
            result = self.base_result(line, report_date)
            if not self.configured:
                result.identity_status = "not_configured"
                result.blockers.append(f"missing_secret:{self.secret_env}")
            else:
                result.identity_status = "registry_declared_secondary_price_source_identity_not_queried"
            results[line.basket_id] = result
        return results

    def fetch_close(self, line: engine.InstrumentLine, report_date: date) -> engine.ProviderResult:
        allocation_candidate = line.basket_id in _ALLOCATION_CANDIDATE_BASKET_IDS
        if line.funded or allocation_candidate:
            result = super().fetch_close(line, report_date)
            if allocation_candidate and not line.funded:
                result.blockers = [
                    blocker
                    for blocker in (result.blockers or [])
                    if blocker != "alpha_vantage_live_close_reserved_for_funded_positions"
                ]
            return result
        result = self.base_result(line, report_date)
        if not self.configured:
            result.pricing_status = "not_configured"
            result.blockers.append(f"missing_secret:{self.secret_env}")
            return result
        result.pricing_status = "skipped_unfunded_capacity_preservation"
        result.blockers.append("alpha_vantage_live_close_reserved_for_funded_or_explicit_allocation_candidates")
        return result


def install_funded_only_alpha_policy(allocation_candidate_basket_ids: list[str] | None = None) -> None:
    """Install the governed funded-plus-explicit-candidate capacity policy."""
    global _ALLOCATION_CANDIDATE_BASKET_IDS
    _ALLOCATION_CANDIDATE_BASKET_IDS = {
        str(value).strip() for value in (allocation_candidate_basket_ids or []) if str(value).strip()
    }
    engine.ADAPTERS["alpha_vantage"] = GovernedAlphaVantageAdapter
