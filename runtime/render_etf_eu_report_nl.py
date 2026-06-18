from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_PRICING = Path("output/pricing/etf_eu_ucits_closing_price_smoke_20260618_000000.json")
DEFAULT_SOURCE_REPORT = Path("output/weekly_etf_eu_review_260618_draft.md")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON root must be an object: {path}")
    return payload


def _pricing_rows(pricing: dict[str, Any]) -> str:
    rows = [
        "| fondsnaam | ISIN | beurs-ticker | Yahoo-symbool | slotdatum | slotkoers | handelsvaluta | bronvaluta | bronbeurs |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in pricing.get("prices") or []:
        rows.append(
            "| {fund_name} | {isin} | {exchange_ticker} | {pricing_symbol} | {close_date} | {close} | {trading_currency} | {source_currency} | {source_exchange} |".format(
                fund_name=row.get("fund_name", ""),
                isin=row.get("isin", ""),
                exchange_ticker=row.get("exchange_ticker", ""),
                pricing_symbol=row.get("pricing_symbol", ""),
                close_date=row.get("close_date", ""),
                close=row.get("close", ""),
                trading_currency=row.get("trading_currency", ""),
                source_currency=row.get("source_currency", ""),
                source_exchange=row.get("source_exchange", ""),
            )
        )
    return "\n".join(rows)


def render_dutch_companion(*, pricing_artifact_path: Path = DEFAULT_PRICING, source_report_path: Path = DEFAULT_SOURCE_REPORT) -> str:
    pricing = _load_json(pricing_artifact_path)
    summary = pricing.get("summary", {}) if isinstance(pricing.get("summary"), dict) else {}
    return f"""# ETF EU-review — volwassen Nederlandse conceptversie

## 1. Status van dit concept

Deze Nederlandse companion is review-only en afgeleid van de Engelse/EU-bronartefacten. Dit is geen zelfstandig nieuw onderzoek.

```text
review-only
geen productielevering
geen e-mailverzending
geen ontvangers geactiveerd
geen portefeuillemutatie
geen financieringsautoriteit
geen waarderingsautoriteit
```

## 2. Kernsamenvatting

De EU-repository heeft bewezen dat de eerste UCITS-beurslijnen via de directe Yahoo chart-bron bruikbare slotkoersen kunnen opleveren. De gebruikte prijsrun bevat {summary.get('prices_found')} gevonden prijzen, {summary.get('pricing_symbols_attempted')} geteste prijssymbolen en {summary.get('source_errors')} bronfouten.

Deze prijsinformatie is bronbewijs. Het is geen waarderingsautoriteit, geen financieringsautoriteit, geen portefeuillemutatie en geen leveringsbewijs.

## 3. UCITS-prijsbewijs

Gebruikte prijsbron: `{pricing_artifact_path}`

{_pricing_rows(pricing)}

Bron- en versheidsbeperking: de koersen komen uit de directe Yahoo chart-bron als dagelijkse slotkoers voor UCITS-beurslijnen. De rapportage gebruikt de laatste niet-lege slotkoers uit het vastgelegde smoke-artefact.

## 4. UCITS-identiteit

| register-id | fondsnaam | ISIN | beurs | beurs-ticker | handelsvaluta | Yahoo-symbool | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| core_us_equity_cspx | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | London Stock Exchange | CSPX | USD | CSPX.L | bevestigd |
| core_us_equity_cspx | iShares Core S&P 500 UCITS ETF USD (Acc) | IE00B5BMR087 | Xetra | SXR8 | EUR | SXR8.DE | bevestigd |

## 5. Scheiding tussen UCITS-kandidaat en Amerikaanse researchproxy

Amerikaanse ETF's zijn alleen researchproxy's en geen belegbare EU-posities.

| UCITS-register-id | Amerikaanse researchproxy | doel |
| --- | --- | --- |
| core_us_equity_cspx | SPY | benchmarkreferentie |

SPY mag alleen worden gebruikt als benchmarkreferentie of onderzoeksvergelijking. SPY is geen EU-belegging in deze rapportage.

## 6. EU-besliscockpit

- **Conceptstatus:** review-only; geen productielevering en geen portefeuillemutatie.
- **Prijsbasis:** UCITS-beurslijnslotkoersen uit het vastgelegde smoke-artefact.
- **Belangrijkste grens:** Amerikaanse ETF's blijven researchproxy's, geen EU-posities.
- **Volgende stap:** HTML/PDF-renderdry-run vanuit volwassen tweetalige rapporten, zonder ontvangers.

## 7. Open punten voor productiegebruik

- Bredere UCITS-dekking.
- KID/PRIIPs-validatie voor de volledige belegbare set.
- Liquiditeit, spread, beursgeschiktheid en TER-verrijking.
- Waarderingspoort met meerdere bronnen.
- Nederlandse taalcontrole en tweetalige pariteit.
- HTML/PDF-renderdry-run zonder ontvangers.
- Expliciet leveringsbeleid met manifest of ontvangstbewijs voordat levering ooit productiestatus krijgt.

## 8. Volgende ontwikkelstap

```text
WP14J — ETF EU HTML/PDF render dry run from mature bilingual reports, no recipients
```

Levering blijft geblokkeerd. Deze Nederlandse companion is uitsluitend een volwassen conceptoppervlak.

## 9. Autoriteitsdisclaimer

Geen productielevering. Geen e-mailverzending. Geen ontvangers geactiveerd. Geen portefeuillemutatie. Geen kandidaat gepromoveerd naar financierbaar. Geen financieringsautoriteit. Geen waarderingsautoriteit. Yahoo-prijsinformatie is bronbewijs en geen zelfstandige waarderingsautoriteit.

Bronrapport: `{source_report_path}`
"""


def write_dutch_companion(output_path: Path, **kwargs: Any) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_dutch_companion(**kwargs), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--pricing-artifact", default=str(DEFAULT_PRICING))
    parser.add_argument("--source-report", default=str(DEFAULT_SOURCE_REPORT))
    args = parser.parse_args()
    output = write_dutch_companion(
        Path(args.output),
        pricing_artifact_path=Path(args.pricing_artifact),
        source_report_path=Path(args.source_report),
    )
    print(f"ETF_EU_DUTCH_COMPANION_RENDERED | output={output}")


if __name__ == "__main__":
    main()
