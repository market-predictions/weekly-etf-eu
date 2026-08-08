from __future__ import annotations

from datetime import date

from pricing import ucits_price_provider_engine as engine


class FundedOnlyAlphaVantageAdapter(engine.AlphaVantageAdapter):
    """Quota-aware Alpha Vantage adapter for the governed ETF EU pricing gate.

    Alpha Vantage's free service is a scarce secondary close source. Exact-line
    identity is anchored independently by Yahoo Chart metadata under the WP11A
    policy, so Alpha SYMBOL_SEARCH calls add no funded-gate authority. This
    adapter therefore avoids Alpha identity-search traffic and reserves daily
    close requests for authoritative funded positions only.
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
        if line.funded:
            return super().fetch_close(line, report_date)
        result = self.base_result(line, report_date)
        if not self.configured:
            result.pricing_status = "not_configured"
            result.blockers.append(f"missing_secret:{self.secret_env}")
            return result
        result.pricing_status = "skipped_unfunded_capacity_preservation"
        result.blockers.append("alpha_vantage_live_close_reserved_for_funded_positions")
        return result


def install_funded_only_alpha_policy() -> None:
    """Install the governed capacity policy into the shared provider engine."""
    engine.ADAPTERS["alpha_vantage"] = FundedOnlyAlphaVantageAdapter
