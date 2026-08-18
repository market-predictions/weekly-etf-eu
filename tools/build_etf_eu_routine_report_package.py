from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pricing.ucits_close_price_validation_contract_v2 import validate_artifact as validate_v2_pricing
from runtime.render_etf_eu_client_report import render_report
from runtime.scrub_etf_eu_client_surface import sanitize_text

SOURCE_REPO = "market-predictions/weekly-etf-eu"
DONOR_REPO = "market-predictions/weekly-etf"
UPSTREAM_PATTERN = (
    "weekly-etf native client-language generation, deterministic state-label normalization, "
    "forbidden-token validation, Mistune semantic HTML, WeasyPrint PDF generation and Poppler validation "
    "adapted for EU routine production"
)

STATUS_LABELS = {
    "nl": {
        "fresh_exact_verified": "Exacte slotkoers, onafhankelijk geverifieerd",
        "fresh_exact_unverified": "Exacte slotkoers, niet onafhankelijk geverifieerd",
        "provider_disagreement": "Prijsconflict tussen bronnen",
        "no_exact_close": "Exacte slotkoers niet beschikbaar",
        "identity_binding_failed": "Handelslijnidentiteit niet geverifieerd",
        "verified_ucits_trading_line": "UCITS-handelslijn geverifieerd",
        "candidate_requires_verification": "Handelslijn nog te verifiëren",
        "fetch_failed": "Prijs niet beschikbaar",
        "blocked": "Prijs geblokkeerd",
        "priced_non_authoritative": "Marktprijs beschikbaar",
    },
    "en": {
        "fresh_exact_verified": "Exact close, independently verified",
        "fresh_exact_unverified": "Exact close, not independently verified",
        "provider_disagreement": "Price disagreement between sources",
        "no_exact_close": "Exact close unavailable",
        "identity_binding_failed": "Trading-line identity not verified",
        "verified_ucits_trading_line": "Verified UCITS trading line",
        "candidate_requires_verification": "Trading line requires verification",
        "fetch_failed": "Price unavailable",
        "blocked": "Price blocked",
        "priced_non_authoritative": "Market price available",
    },
}

PRIMARY_VERIFICATION_STATUSES = {
    "fresh_exact_verified",
    "fresh_exact_unverified",
    "provider_disagreement",
    "no_exact_close",
    "identity_binding_failed",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Required JSON input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _price(value: object) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "n/a"


def _pricing_rows(pricing: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in pricing.get("rows", []) if isinstance(row, dict)]
    return sorted(rows, key=lambda row: (str(row.get("fund_name") or ""), str(row.get("ticker") or "")))


def _latest_close_date(rows: list[dict[str, Any]]) -> str | None:
    dates = sorted({str(row.get("close_date")) for row in rows if row.get("close_date")})
    return dates[-1] if dates else None


def _status_label(row: dict[str, Any], *, language: str) -> str:
    pricing_status = str(row.get("pricing_status") or "").strip()
    authority_status = str(row.get("source_agreement_status") or "").strip()
    verification_status = str(row.get("verification_status") or "").strip()
    mapping = STATUS_LABELS[language]

    # Primary+verification authority is the client-relevant status. It tells the
    # reader whether the exact close had an independent current verifier; stable
    # UCITS line identity is a separate static contract and must not be conflated
    # with missing second-source price verification.
    candidates = []
    if authority_status in PRIMARY_VERIFICATION_STATUSES:
        candidates.append(authority_status)
    if pricing_status == "fetch_failed":
        candidates.append("fetch_failed")
    candidates.extend([verification_status, pricing_status])
    for source in candidates:
        if source in mapping:
            return mapping[source]
    source = next((item for item in candidates if item), "missing")
    raise SystemExit(f"Unknown client-surface status enum: {source}")


def _table(rows: list[dict[str, Any]], *, dutch: bool) -> str:
    language = "nl" if dutch else "en"
    if dutch:
        lines = [
            "| Handelslijn | ISIN | Markt | Slot | Valuta | Status |",
            "|---|---|---|---:|---|---|",
        ]
    else:
        lines = [
            "| Trading line | ISIN | Market | Close | Currency | Status |",
            "|---|---|---|---:|---|---|",
        ]
    for row in rows:
        ticker = str(row.get("ticker") or "n/a")
        exchange = str(row.get("exchange") or "n/a")
        isin = str(row.get("isin") or "n/a")
        status = _status_label(row, language=language)
        lines.append(
            f"| {ticker} · {exchange} | {isin} | {row.get('close_date') or 'n/a'} | "
            f"{_price(row.get('close_price'))} | {row.get('currency') or 'n/a'} | {status} |"
        )
    return "\n".join(lines)


def _lane_summary(rows: list[dict[str, Any]], *, dutch: bool) -> str:
    priced = [
        row
        for row in rows
        if row.get("pricing_status") == "priced_non_authoritative" and row.get("close_price") is not None
    ]
    verified = [row for row in priced if row.get("source_agreement_status") == "fresh_exact_verified"]
    unverified = [row for row in priced if row.get("source_agreement_status") == "fresh_exact_unverified"]
    legacy_verified = [
        row
        for row in priced
        if row.get("source_agreement_status") not in PRIMARY_VERIFICATION_STATUSES
        and row.get("verification_status") == "verified_ucits_trading_line"
    ]
    other_priced = [
        row for row in priced if row not in verified and row not in unverified and row not in legacy_verified
    ]
    unresolved = [row for row in rows if row not in priced]
    if dutch:
        lines = [
            f"- **Prijsdekking:** {len(priced)} van {len(rows)} handelslijnen geprijsd.",
            f"- **Exacte slotkoersen met onafhankelijke actuele verificatie:** {len(verified)}.",
            f"- **Exacte slotkoersen zonder tweede actuele verifier:** {len(unverified)}.",
        ]
        if legacy_verified:
            lines.append(f"- **Legacy geverifieerde handelslijnen:** {len(legacy_verified)}.")
        if other_priced:
            lines.append(f"- **Overige geprijsde onderzoekslijnen:** {len(other_priced)}.")
        lines.extend(
            [
                f"- **Geblokkeerd of niet opgelost:** {len(unresolved)}.",
                "- **Portefeuillebesluit:** prijsverificatie wijzigt op zichzelf geen portefeuille- of allocatiebesluit.",
            ]
        )
        return "\n".join(lines)
    lines = [
        f"- **Pricing coverage:** {len(priced)} of {len(rows)} trading lines priced.",
        f"- **Exact closes with independent current verification:** {len(verified)}.",
        f"- **Exact closes without a second current verifier:** {len(unverified)}.",
    ]
    if legacy_verified:
        lines.append(f"- **Legacy verified trading lines:** {len(legacy_verified)}.")
    if other_priced:
        lines.append(f"- **Other priced research lines:** {len(other_priced)}.")
    lines.extend(
        [
            f"- **Blocked or unresolved:** {len(unresolved)}.",
            "- **Portfolio decision:** price verification by itself does not change any portfolio or allocation decision.",
        ]
    )
    return "\n".join(lines)


def _markdown_nl(report_date: str, state: dict[str, Any], pricing: dict[str, Any]) -> str:
    rows = _pricing_rows(pricing)
    latest = _latest_close_date(rows) or "niet beschikbaar"
    return f"""# Weekly ETF EU Review | Nederlands | {report_date}

> **Routine productie-review.** Prijspeildatum: {latest}. De EU-portefeuille blijft ISIN-first. Amerikaanse ETF-symbolen dienen uitsluitend als onderzoeksreferentie en zijn binnen dit model niet investeerbaar.

## 1. Besluit in één oogopslag

- **Actie:** geen transactie; EUR 100.000 cash behouden.
- **Reden:** de portefeuille bevat nog geen gefinancierde UCITS-posities en de huidige prijsrun levert marktobservaties, geen zelfstandige basis voor aankoop of waardering.
- **Beste operationele kandidaat:** de geverifieerde S&P 500 UCITS-lijnen blijven het verst gevorderd voor verdere bevestiging bij de broker en van de handelslijn.
- **Niet doen:** do not allocate capital to thematic or gold exposure until identity, KID, trading-line and product-policy checks are complete.

## 2. Portefeuille en kapitaal

| Component | Waarde |
|---|---:|
| Startkapitaal | EUR {_price(state.get('starting_capital_eur'))} |
| Cash | EUR {_price(state.get('cash_eur'))} |
| Belegde marktwaarde | EUR {_price(state.get('invested_market_value_eur'))} |
| Totale portefeuillewaarde | EUR {_price(state.get('nav_eur'))} |
| Gefinancierde posities | {len(state.get('positions') or [])} |

## 3. Actuele UCITS-prijssnapshot

{_table(rows, dutch=True)}

De getoonde prijzen zijn marktobservaties uit de huidige routine-run en vormen geen zelfstandige basis voor waardering of aankoop.

## 4. Dekking en besliskwaliteit

{_lane_summary(rows, dutch=True)}

## 5. Lane-oordeel

- **Core-aandelen:** operationeel het meest volwassen; SXR8 en CSPX blijven onderzoekskandidaten en zijn niet gefinancierd.
- **Wereldwijde aandelen:** IWDA, EUNL en VWCE blijven interessant voor brede spreiding, maar verificatie van handelslijn en bron is nog niet volledig.
- **Technologie en halfgeleiders:** SXRV, CNDX en SMH bieden hogere bèta en concentratierisico; geen inzet van kapitaal vóór volledige verificatie.
- **Obligaties:** EUNA en AGGH kunnen later stabiliteit leveren; hun huidige rol blijft die van onderzoekskandidaat.
- **Goud:** Europese blootstelling betreft vaak ETC-structuren en blijft geblokkeerd binnen het beleid dat uitsluitend UCITS-fondsen toestaat, totdat een expliciete beleidsbeslissing bestaat.

## 6. Risico- en kwaliteitsgrenzen

1. Een prijsobservatie is geen zelfstandige waarderingsbasis.
2. Een ticker is geen canonieke identiteit; ISIN blijft leidend.
3. Geen portefeuillewijziging zonder een afzonderlijk besluit over inzet van kapitaal.
4. Vorige rapporten zijn historische strategiecontext, niet actuele prijswaarheid.
5. Onopgeloste lijnen blijven buiten de besluitvorming voor de cliënt.
"""


def _markdown_en(report_date: str, state: dict[str, Any], pricing: dict[str, Any]) -> str:
    rows = _pricing_rows(pricing)
    latest = _latest_close_date(rows) or "unavailable"
    return f"""# Weekly ETF EU Review | English | {report_date}

> **Routine production review.** Pricing date: {latest}. The EU portfolio remains ISIN-first. U.S. ETF symbols are research references only and are not investable within this model.

## 1. Decision at a glance

- **Action:** no transaction; retain EUR 100,000 cash.
- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not an independent basis for purchase or valuation.
- **Most advanced operational candidate:** the verified S&P 500 UCITS lines remain furthest advanced for broker and trading-line confirmation.
- **Do not:** allocate capital to thematic or gold exposure until identity, KID, trading-line and product-policy checks are complete.

## 2. Portfolio and capital

| Component | Value |
|---|---:|
| Starting capital | EUR {_price(state.get('starting_capital_eur'))} |
| Cash | EUR {_price(state.get('cash_eur'))} |
| Invested market value | EUR {_price(state.get('invested_market_value_eur'))} |
| Total portfolio value | EUR {_price(state.get('nav_eur'))} |
| Funded positions | {len(state.get('positions') or [])} |

## 3. Current UCITS pricing snapshot

{_table(rows, dutch=False)}

The displayed prices are market observations from the current routine run and do not by themselves create purchase, allocation or portfolio authority.

## 4. Coverage and decision quality

{_lane_summary(rows, dutch=False)}

## 5. Lane view

- **Core equity:** operationally the most mature; SXR8 and CSPX remain research candidates and are not funded.
- **Global equity:** IWDA, EUNL and VWCE remain interesting for broad diversification, but trading-line and source verification is not yet complete for all research lines.
- **Technology and semiconductors:** SXRV, CNDX and SMH carry higher beta and concentration risk; no capital deployment before full verification.
- **Bonds:** EUNA and AGGH may later add stability; their current role in this broad table remains research context unless already present in the protected funded portfolio.
- **Gold:** European exposure is often implemented through ETC structures and remains blocked under the UCITS-fund-only policy unless an explicit policy decision changes that boundary.

## 6. Risk and quality boundaries

1. A price observation does not by itself create portfolio or allocation authority.
2. A ticker is not canonical identity; ISIN remains authoritative.
3. No portfolio change without a separate capital-allocation decision.
4. Prior reports are historical strategy context, not current-price truth.
5. Unresolved lines stay outside client decision authority.
"""


def build(args: argparse.Namespace) -> dict[str, Path]:
    pricing_path = Path(args.pricing_artifact)
    portfolio_state_path = Path(args.portfolio_state)
    pricing_validation = validate_v2_pricing(
        pricing_path,
        expected_report_date=args.report_date,
        portfolio_state_path=portfolio_state_path,
        require_funded_consensus=True,
    )
    if pricing_validation["valid"] is not True:
        raise SystemExit(
            "Canonical v2 pricing contract failed before report package build: "
            + "; ".join(pricing_validation["blockers"])
        )

    pricing = _load_json(pricing_path)
    state = _load_json(portfolio_state_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    nl_md = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.md"
    en_md = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.md"
    nl_html = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.html"
    en_html = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.html"
    nl_pdf = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.pdf"
    en_pdf = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.pdf"

    nl_text, nl_sanitization = sanitize_text(_markdown_nl(args.report_date, state, pricing), language="nl")
    en_text, en_sanitization = sanitize_text(_markdown_en(args.report_date, state, pricing), language="en")
    nl_md.write_text(nl_text, encoding="utf-8")
    en_md.write_text(en_text, encoding="utf-8")

    render_report(
        markdown_path=nl_md,
        html_output=nl_html,
        pdf_output=nl_pdf,
        language="nl",
        title=f"Weekly ETF EU Review — {args.report_date}",
    )
    render_report(
        markdown_path=en_md,
        html_output=en_html,
        pdf_output=en_pdf,
        language="en",
        title=f"Weekly ETF EU Review — {args.report_date}",
    )

    manifest = {
        "schema_version": "etf_eu_routine_report_package_v1",
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "pricing_artifact": str(pricing_path),
        "pricing_contract_validation": pricing_validation,
        "portfolio_state": str(portfolio_state_path),
        "portfolio_mutation": False,
        "real_broker_execution": False,
        "smtp_send": False,
        "delivery_authority": False,
        "artifacts": {
            "nl_markdown": str(nl_md),
            "en_markdown": str(en_md),
            "nl_html": str(nl_html),
            "en_html": str(en_html),
            "nl_pdf": str(nl_pdf),
            "en_pdf": str(en_pdf),
        },
        "sanitization": {
            "nl": nl_sanitization,
            "en": en_sanitization,
        },
        "upstream_pattern": UPSTREAM_PATTERN,
        "donor_repository": DONOR_REPO,
        "source_repository": SOURCE_REPO,
    }
    manifest_path = output_dir / f"etf_eu_routine_report_package_manifest_{args.run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "nl_markdown": nl_md,
        "en_markdown": en_md,
        "nl_html": nl_html,
        "en_html": en_html,
        "nl_pdf": nl_pdf,
        "en_pdf": en_pdf,
        "manifest": manifest_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--portfolio-state", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    outputs = build(args)
    print(
        "ETF_EU_ROUTINE_REPORT_PACKAGE_OK"
        f" | nl_pdf={outputs['nl_pdf']}"
        f" | en_pdf={outputs['en_pdf']}"
        " | portfolio_mutation=false | smtp_send=false"
    )


if __name__ == "__main__":
    main()
