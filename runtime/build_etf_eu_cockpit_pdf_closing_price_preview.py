from __future__ import annotations

import json
from pathlib import Path

RUN_ID = "20260703_000000"
SOURCE = Path("output/client_surface/etf_eu_closing_price_poc_20260703_000000.json")
REPAIR = Path("output/client_surface/etf_eu_closing_price_poc_provider_repair_20260703_000000.json")
MARKDOWN = Path("output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.md")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.json")
PDF = Path("output/client_surface/etf_eu_cockpit_closing_price_preview_20260703_000000.pdf")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown(data: dict) -> str:
    return f"""# ETF EU Cockpit - Closing Price Preview

## Wat dit nu bewijst

De EU cockpit kan nu een echte, ISIN-first UCITS handelslijn tonen met een provider-slotkoers. Dit is het eerste zichtbare koersbewijs in de review-surface.

## Eerste koers-POC

| ISIN | Fonds | Handelslijn | Valuta | Slotdatum | Slotkoers | Bron | Status |
|---|---|---|---|---:|---:|---|---|
| {data['isin']} | {data['fund_name']} | {data['pricing_symbol']} | {data['trading_currency']} | {data['latest_close_date']} | {data['latest_close']} | {data['pricing_source']} | {data['provider_status']} |

## Visuele cockpitkaart

```text
Eerste koers-POC - niet waarderingsgeschikt / niet leveringsgereed
SXR8.DE / IE00B5BMR087 / EUR
Slotdatum: {data['latest_close_date']}
Slotkoers: {data['latest_close']}
Bron: {data['pricing_source']}
Status: {data['provider_status']}
```

## Wat dit nog niet bewijst

Dit is een beperkte koers-POC. Dit is geen waarderingsgeschikte prijsbasis, geen client-grade rapportbewijs en geen leveringsautorisatie.

Het bewijst ook geen funding, portefeuillewijziging, kandidaatpromotie of productiepad.

## Volgende stap

ETF-EU-WP15AA - breid deze zichtbare koerskaart uit naar een kleine multi-line UCITS pricing preview met uitsluitend geverifieerde EU-symbolen.
"""


def build() -> dict:
    data = _load(SOURCE)
    _load(REPAIR)
    MARKDOWN.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN.write_text(_markdown(data), encoding="utf-8")
    artifact = {
        "schema_version": "etf_eu_cockpit_closing_price_preview_v1",
        "run_id": RUN_ID,
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15Z",
        "source_work_package": "ETF-EU-WP15Y-FIX",
        "source_pricing_artifact": str(SOURCE),
        "source_repair_artifact": str(REPAIR),
        "source_preview_artifact": "output/client_surface/etf_eu_closing_price_poc_preview_20260703_000000.md",
        "markdown_preview_path": str(MARKDOWN),
        "pdf_preview_path": str(PDF),
        "pdf_created": PDF.exists(),
        "preview_surface_created": True,
        "symbol": data["symbol"],
        "isin": data["isin"],
        "fund_name": data["fund_name"],
        "exchange": data["exchange"],
        "exchange_ticker": data["exchange_ticker"],
        "trading_currency": data["trading_currency"],
        "latest_close_date": data["latest_close_date"],
        "latest_close": data["latest_close"],
        "pricing_source": data["pricing_source"],
        "pricing_fetch_timestamp": data["pricing_fetch_timestamp"],
        "provider_status": data["provider_status"],
        "pricing_poc_status": data["pricing_poc_status"],
        "review_only": True,
        "valuation_grade": False,
        "pricing_evidence_for_client_grade": False,
        "pricing_evidence_for_delivery_preflight": False,
        "production_delivery": False,
        "portfolio_mutation": False,
        "candidate_promotion": False,
        "funding_authority": False,
        "client_grade_claim": False,
        "delivery_ready": False,
        "delivery_preflight_allowed": False,
        "receipt_artifact_created": False,
        "production_manifest_created": False,
        "fake_price_used": False,
        "us_proxy_price_used": False,
        "selected_next_package": "ETF-EU-WP15AA",
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
