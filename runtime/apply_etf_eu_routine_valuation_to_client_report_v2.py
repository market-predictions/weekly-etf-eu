from __future__ import annotations

from runtime import apply_etf_eu_routine_valuation_to_client_report as legacy

_original_build_current_performance = legacy.build_current_performance


def build_current_performance_with_fallback_labels(soup, state, lang):
    try:
        return _original_build_current_performance(soup, state, lang)
    except RuntimeError as exc:
        message = str(exc)
        if not message.startswith("Performance-table source labels missing for:"):
            raise
        # The legacy builder has already rendered the complete current table with
        # deterministic ticker/fund-name fallback labels before raising. A newly
        # activated exact-line model position is therefore retained rather than
        # being suppressed solely because the historical source report had no row.
        table = soup.find("table", class_="routine-current-performance-table")
        if table is None:
            raise
        table["data-new-position-label-fallback"] = "true"
        return None


def main() -> None:
    legacy.build_current_performance = build_current_performance_with_fallback_labels
    legacy.main()


if __name__ == "__main__":
    main()
