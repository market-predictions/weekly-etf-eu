from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

REQUIRED_AUTHORITY_LINES = [
    "review_only=true",
    "production_delivery=false",
    "portfolio_mutation=false",
    "funding_authority=false",
    "valuation_grade=false",
]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"YAML root must be an object: {path}")
    return payload


def _cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _find_trading_line(registry: dict[str, Any], pricing_symbol: str) -> tuple[dict[str, Any], dict[str, Any]]:
    for fund in registry.get("funds") or []:
        if not isinstance(fund, dict):
            continue
        for line in fund.get("trading_lines") or []:
            if not isinstance(line, dict):
                continue
            if str(line.get("pricing_symbol_yahoo", "")).strip() == pricing_symbol:
                return fund, line
    return {}, {}


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        output.append("| " + " | ".join(_cell(value) for value in row) + " |")
    return "\n".join(output)


def build_report(*, registry_path: Path, pricing_artifact_path: Path) -> str:
    registry = _load_yaml(registry_path)
    pricing = _load_json(pricing_artifact_path)
    prices = pricing.get("prices") or []
    failures = pricing.get("failures") or []
    if not prices:
        raise RuntimeError("WP14F requires at least one committed UCITS price row")

    pricing_rows: list[list[Any]] = []
    identity_rows: list[list[Any]] = []
    proxy_rows: list[list[Any]] = []
    seen_proxy_rows: set[tuple[str, str, str]] = set()

    for row in prices:
        if not isinstance(row, dict):
            continue
        pricing_rows.append(
            [
                row.get("fund_name"),
                row.get("isin"),
                row.get("exchange_ticker"),
                row.get("pricing_symbol"),
                row.get("close_date"),
                row.get("close"),
                row.get("trading_currency"),
                row.get("source_currency", ""),
                row.get("source_exchange", ""),
                row.get("source"),
            ]
        )
        fund, line = _find_trading_line(registry, str(row.get("pricing_symbol", "")))
        identity_rows.append(
            [
                fund.get("registry_id", row.get("registry_id")),
                fund.get("fund_name", row.get("fund_name")),
                fund.get("isin", row.get("isin")),
                line.get("exchange", row.get("exchange")),
                line.get("exchange_ticker", row.get("exchange_ticker")),
                line.get("trading_currency", row.get("trading_currency")),
                line.get("pricing_symbol_yahoo", row.get("pricing_symbol")),
                fund.get("ucits_status", ""),
                fund.get("priips_kid_status", ""),
                fund.get("investability_status", ""),
            ]
        )
        for proxy in fund.get("research_proxies") or []:
            if not isinstance(proxy, dict):
                continue
            proxy_tuple = (
                str(fund.get("registry_id", "")),
                str(proxy.get("us_proxy", "")),
                str(proxy.get("purpose", "")),
            )
            if proxy_tuple in seen_proxy_rows:
                continue
            seen_proxy_rows.add(proxy_tuple)
            proxy_rows.append(
                [
                    fund.get("registry_id", ""),
                    fund.get("fund_name", ""),
                    proxy.get("us_proxy", ""),
                    proxy.get("purpose", ""),
                    proxy.get("proxy_must_not_be_funded", ""),
                ]
            )

    skipped_rows = [
        [failure.get("registry_id"), failure.get("exchange_ticker"), failure.get("pricing_symbol"), failure.get("status"), failure.get("reason")]
        for failure in failures
        if isinstance(failure, dict)
    ]

    pricing_table = _markdown_table(
        [
            "fund_name",
            "isin",
            "exchange_ticker",
            "pricing_symbol",
            "close_date",
            "close",
            "trading_currency",
            "source_currency",
            "source_exchange",
            "source",
        ],
        pricing_rows,
    )
    identity_table = _markdown_table(
        [
            "registry_id",
            "fund_name",
            "isin",
            "exchange",
            "exchange_ticker",
            "trading_currency",
            "pricing_symbol_yahoo",
            "ucits_status",
            "priips_kid_status",
            "investability_status",
        ],
        identity_rows,
    )
    proxy_table = _markdown_table(
        ["registry_id", "fund_name", "us_research_proxy", "purpose", "proxy_must_not_be_funded"],
        proxy_rows,
    )
    skipped_table = _markdown_table(
        ["registry_id", "exchange_ticker", "pricing_symbol", "status", "reason"],
        skipped_rows,
    )

    summary = pricing.get("summary", {})
    report = f"""# ETF EU Review — First UCITS Pricing Draft

## 1. ETF EU Review — Draft status

```text
review_only=true
production_delivery=false
portfolio_mutation=false
funding_authority=false
valuation_grade=false
```

This is the first review-only ETF EU markdown draft generated from UCITS identity and committed UCITS closing-price smoke evidence.

## 2. Executive summary

The EU repository has now proven first live UCITS closing-price retrieval through the direct Yahoo chart endpoint for the first tested UCITS exchange-line symbols. The committed smoke artifact records `{summary.get('prices_found')}` successful price rows, `{summary.get('pricing_symbols_attempted')}` attempted pricing symbols, `{summary.get('symbols_skipped')}` skipped pending symbols, and `{summary.get('source_errors')}` source errors.

Yahoo chart pricing is source evidence only. It is not valuation-grade authority by itself, not funding authority, not portfolio mutation authority, and not delivery authority.

## 3. UCITS pricing evidence used

Pricing artifact used:

```text
{pricing_artifact_path}
```

{pricing_table}

Source/freshness disclosure: the prices above come from the direct Yahoo chart endpoint as daily close evidence for UCITS exchange-line symbols. The report uses the latest non-null close present in the committed smoke artifact. This pricing path is technically viable for the first tested symbols, but broader universe coverage, independent source agreement, and valuation-grade gate promotion remain open.

## 4. Instrument identity table

Registry used:

```text
{registry_path}
```

{identity_table}

## 5. Research proxy separation

U.S. ETFs are research proxies only and are not EU investable holdings.

{proxy_table}

The U.S. research proxy symbols above may be used only as benchmark references, thematic comparators, or historical signal inputs. They are not funded EU holdings and must not be written into EU portfolio state as investable instruments.

## 6. Initial observations

- The first two UCITS lines now have usable close evidence.
- The pricing source path is technically viable for the first tested UCITS exchange-line symbols.
- Further universe expansion is still needed before a broader EU report can be considered complete.
- The current evidence supports report-surface review only and does not create funding, portfolio, valuation-grade, or delivery authority.

Skipped or unavailable lines from the smoke artifact:

{skipped_table}

## 7. Open gaps before production use

- Broader UCITS coverage.
- KID/PRIIPs validation across the investable universe.
- Liquidity, spread, exchange suitability and TER enrichment.
- Valuation-grade agreement gate and source policy promotion.
- Bilingual runtime port from the mature weekly-etf report path.
- Dutch language quality gate.
- Delivery/PDF dry run.
- Receipt/manifest path for any later production delivery claim.

## 8. Next development step

The next planned package is:

```text
WP14G — Port weekly-etf runtime/bilingual/report-quality layers into weekly-etf-eu
```

This should start only after the first draft report baseline is committed and reviewed. The porting rule remains: port behavior, not U.S. assumptions.

## 9. Authority and delivery disclaimer

This report is review-only.
No production delivery occurred.
No email was sent.
No PDF production delivery was generated.
No recipient was activated.
No portfolio mutation occurred.
No candidate was promoted to fundable.
Yahoo chart pricing is source evidence only and not valuation-grade authority by itself.
"""
    return report


def render_report(*, registry_path: Path, pricing_artifact_path: Path, output_path: Path) -> Path:
    report = build_report(registry_path=registry_path, pricing_artifact_path=pricing_artifact_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = render_report(
        registry_path=Path(args.registry),
        pricing_artifact_path=Path(args.pricing_artifact),
        output_path=Path(args.output),
    )
    print(f"ETF_EU_DRAFT_REPORT_RENDERED | output={output}")


if __name__ == "__main__":
    main()
