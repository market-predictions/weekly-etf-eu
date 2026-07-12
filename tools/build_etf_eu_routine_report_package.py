from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.render_etf_eu_client_report import render_report


SOURCE_REPO = "market-predictions/weekly-etf-eu"
DONOR_REPO = "market-predictions/weekly-etf"
UPSTREAM_PATTERN = (
    "weekly-etf Markdown preprocessing, Mistune table rendering, semantic HTML, "
    "WeasyPrint PDF generation and Poppler validation adapted for EU routine production"
)


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


def _table(rows: list[dict[str, Any]], *, dutch: bool) -> str:
    if dutch:
        lines = [
            "| Trading line | ISIN | Markt | Slot | Valuta | Status |",
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
        status = str(row.get("verification_status") or row.get("pricing_status") or "unknown")
        lines.append(
            f"| {ticker} · {exchange} | {isin} | {row.get('close_date') or 'n/a'} | "
            f"{_price(row.get('close_price'))} | {row.get('currency') or 'n/a'} | {status} |"
        )
    return "\n".join(lines)


def _lane_summary(rows: list[dict[str, Any]], *, dutch: bool) -> str:
    priced = [row for row in rows if row.get("pricing_status") == "priced_non_authoritative" and row.get("close_price") is not None]
    verified = [row for row in priced if row.get("verification_status") == "verified_ucits_trading_line"]
    pending = [row for row in priced if row.get("verification_status") != "verified_ucits_trading_line"]
    failed = [row for row in rows if row.get("pricing_status") == "fetch_failed"]
    if dutch:
        return (
            f"- **Prijsdekking:** {len(priced)} van {len(rows)} trading lines geprijsd.\n"
            f"- **Volledig geverifieerde lijnen:** {len(verified)}.\n"
            f"- **Geprijsd maar identiteit/lijn nog te verifiëren:** {len(pending)}.\n"
            f"- **Niet opgelost:** {len(failed)}.\n"
            "- **Portefeuillebesluit:** cash behouden; geen instrument is door deze prijsrun automatisch fundable geworden."
        )
    return (
        f"- **Pricing coverage:** {len(priced)} of {len(rows)} trading lines priced.\n"
        f"- **Fully verified lines:** {len(verified)}.\n"
        f"- **Priced but identity/line verification still pending:** {len(pending)}.\n"
        f"- **Unresolved:** {len(failed)}.\n"
        "- **Portfolio decision:** retain cash; this pricing run did not automatically make any instrument fundable."
    )


def _markdown_nl(report_date: str, state: dict[str, Any], pricing: dict[str, Any]) -> str:
    rows = _pricing_rows(pricing)
    latest = _latest_close_date(rows) or "niet beschikbaar"
    return f"""# Weekly ETF EU Review | Nederlands | {report_date}

> **Routine productie-review.** Prijspeildatum: {latest}. De EU-portefeuille blijft ISIN-first. Amerikaanse ETF-symbolen zijn uitsluitend research proxy en niet investeerbaar binnen dit model.

## 1. Besluit in één oogopslag

- **Actie:** geen transactie; EUR 100.000 cash behouden.
- **Reden:** de portefeuille bevat nog geen gefinancierde UCITS-posities en de huidige prijsrun levert marktobservaties, geen funding- of waarderingsautoriteit.
- **Beste operationele kandidaat:** de geverifieerde S&P 500 UCITS-lijnen blijven het verst gevorderd voor verdere broker- en pricing-line bevestiging.
- **Niet doen:** geen thematische of goudblootstelling financieren zolang identiteit, KID, trading line of productbeleid niet volledig zijn gevalideerd.

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

Prijsdata is connectivity/reference evidence uit de huidige routine-run en blijft `valuation_grade=false`.

## 4. Dekking en besliskwaliteit

{_lane_summary(rows, dutch=True)}

## 5. Lane-oordeel

- **Core aandelen:** operationeel het meest volwassen; SXR8/CSPX blijven research candidates, niet gefinancierd.
- **Wereldwijde aandelen:** IWDA/EUNL/VWCE blijven interessant voor brede spreiding, maar lijn- en bronverificatie is nog niet volledig.
- **Technologie/semiconductors:** SXRV/CNDX/SMH bieden hogere beta en concentratierisico; geen funding vóór volledige verificatie.
- **Obligaties:** EUNA/AGGH kunnen later stabiliteit leveren; huidige rol blijft kandidaat/research.
- **Goud:** Europese blootstelling betreft vaak ETC-structuren; geblokkeerd binnen UCITS-only beleid totdat een expliciete beleidsbeslissing bestaat.

## 6. Risico- en kwaliteitsgrenzen

1. Prijsobservatie is geen waarderingsautoriteit.
2. Een ticker is geen canonieke identiteit; ISIN blijft leidend.
3. Geen portfolio-mutatie zonder afzonderlijke fundingbeslissing.
4. Vorige rapporten zijn historische strategiecontext, niet actuele prijswaarheid.
5. Onopgeloste lijnen blijven buiten de client-facing beslisclaim.

## 7. Volgende routineactie

- Rond verificatie van brokerbeschikbaarheid en EUR-trading lines af.
- Verbeter bronovereenkomst voordat valuation-grade ooit wordt overwogen.
- Herbeoordeel pas daarna of cash gedeeltelijk mag worden ingezet.

## 8. Authority flags

```text
ready_for_controlled_delivery=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```
"""


def _markdown_en(report_date: str, state: dict[str, Any], pricing: dict[str, Any]) -> str:
    rows = _pricing_rows(pricing)
    latest = _latest_close_date(rows) or "unavailable"
    return f"""# Weekly ETF EU Review | English Companion | {report_date}

> **Routine production review.** Pricing date: {latest}. The EU portfolio remains ISIN-first. U.S. ETF symbols are research proxies only and are not investable in this model.

## 1. Decision at a glance

- **Action:** no trade; retain EUR 100,000 cash.
- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not funding or valuation authority.
- **Most advanced operational candidate:** the verified S&P 500 UCITS lines remain furthest advanced for broker and pricing-line confirmation.
- **Avoid:** do not fund thematic or gold exposure until identity, KID, trading line and product-policy checks are complete.

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

Pricing is connectivity/reference evidence from the current routine run and remains `valuation_grade=false`.

## 4. Coverage and decision quality

{_lane_summary(rows, dutch=False)}

## 5. Lane assessment

- **Core equity:** operationally most mature; SXR8/CSPX remain research candidates, not funded.
- **Global equity:** IWDA/EUNL/VWCE remain relevant for broad diversification, but line and source verification is incomplete.
- **Technology/semiconductors:** SXRV/CNDX/SMH carry higher beta and concentration risk; no funding before full verification.
- **Bonds:** EUNA/AGGH may later provide stability; their current role remains candidate/research.
- **Gold:** European exposure often uses ETC structures; blocked under UCITS-only policy until an explicit policy decision exists.

## 6. Risk and quality boundaries

1. A price observation is not valuation authority.
2. A ticker is not canonical identity; ISIN remains authoritative.
3. No portfolio mutation without a separate funding decision.
4. Previous reports are historical strategy context, not current-price truth.
5. Unresolved lines remain outside the client-facing decision claim.

## 7. Next routine action

- Complete broker availability and EUR trading-line verification.
- Improve source agreement before valuation-grade is considered.
- Only then reassess whether part of the cash may be deployed.

## 8. Authority flags

```text
ready_for_controlled_delivery=false
send_executed=false
transport_attempted=false
receipt_confirmed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```
"""


def build(args: argparse.Namespace) -> dict[str, Path]:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    state = _load_json(Path(args.portfolio_state))
    pricing = _load_json(Path(args.pricing_artifact))
    rows = _pricing_rows(pricing)
    if pricing.get("min_threshold_met") is not True or len([r for r in rows if r.get("close_price") is not None]) < 8:
        raise SystemExit("Fresh pricing coverage is insufficient for routine publication")

    nl_md = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.md"
    en_md = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.md"
    nl_html = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.html"
    en_html = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.html"
    nl_pdf = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.pdf"
    en_pdf = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.pdf"
    manifest_path = output_dir / f"etf_eu_fresh_generation_package_manifest_{args.run_id}.json"
    ready_path = output_dir / f"etf_eu_ready_for_controlled_delivery_{args.run_id}.json"
    routine_path = Path("output/run_manifests") / f"etf_eu_routine_run_manifest_{args.report_date}_{args.run_id}.json"

    nl_text = _markdown_nl(args.report_date, state, pricing)
    en_text = _markdown_en(args.report_date, state, pricing)
    nl_md.write_text(nl_text, encoding="utf-8")
    en_md.write_text(en_text, encoding="utf-8")

    render_report(
        markdown_path=nl_md,
        html_output=nl_html,
        pdf_output=nl_pdf,
        language="nl",
        title=f"Weekly ETF EU Review | Nederlands | {args.report_date}",
    )
    render_report(
        markdown_path=en_md,
        html_output=en_html,
        pdf_output=en_pdf,
        language="en",
        title=f"Weekly ETF EU Review | English Companion | {args.report_date}",
    )

    latest_close = _latest_close_date(rows)
    manifest = {
        "schema_version": "etf_eu_fresh_generation_package_v1",
        "artifact_type": "etf_eu_fresh_generation_package_manifest",
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "pricing_as_of": latest_close,
        "source_of_truth_repo": SOURCE_REPO,
        "reference_architecture_repo": DONOR_REPO,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "fresh_generation_status": "full_package_generated",
        "full_generation_status": "client_grade_renderer_integrated",
        "markdown_generation_status": "generated",
        "html_generation_status": "generated",
        "pdf_generation_status": "generated_pending_quality_gates",
        "renderer": "runtime/render_etf_eu_client_report.py",
        "renderer_engine": "weasyprint",
        "markdown_engine": "mistune_table",
        "pdf_machine_gate_passed": False,
        "pdf_visual_gate_passed": False,
        "client_output_valid": False,
        "markdown_output_available": True,
        "html_output_available": True,
        "pdf_output_available": True,
        "dutch_primary": True,
        "english_companion": True,
        "isin_first_identity": True,
        "us_etfs_proxy_only": True,
        "main_surface_us_holdings_exposure": False,
        "nan_price_in_client_surface": False,
        "stale_delivery_wording_present": False,
        "ready_for_controlled_delivery": False,
        "delivery_authorized": False,
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "portfolio_state_path": args.portfolio_state,
        "valuation_history_path": args.valuation_history,
        "trade_ledger_path": args.trade_ledger,
        "recommendation_scorecard_path": args.recommendation_scorecard,
        "pricing_artifact_path": args.pricing_artifact,
        "previous_routine_run_manifest": args.previous_routine_manifest,
        "previous_delivery_closeout_manifest": args.previous_delivery_closeout_manifest,
        "routine_run_manifest": str(routine_path),
        "dutch_primary_markdown": str(nl_md),
        "english_companion_markdown": str(en_md),
        "dutch_primary_html": str(nl_html),
        "english_companion_html": str(en_html),
        "dutch_primary_pdf": str(nl_pdf),
        "english_companion_pdf": str(en_pdf),
        "ready_artifact": str(ready_path),
        "next_action": "RUN_ROUTINE_PDF_QUALITY_GATES",
        "next_package": None,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ready = {
        "schema_version": "etf_eu_ready_for_controlled_delivery_v1",
        "artifact_type": "etf_eu_ready_for_controlled_delivery",
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "fresh_generation_package_manifest": str(manifest_path),
        "pdf_machine_gate_passed": False,
        "pdf_visual_gate_passed": False,
        "client_output_valid": False,
        "ready_for_controlled_delivery": False,
        "delivery_authorized": False,
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "next_action": "RUN_ROUTINE_PDF_QUALITY_GATES",
    }
    ready_path.write_text(json.dumps(ready, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            "tools/write_etf_eu_routine_run_manifest.py",
            "--run-id",
            args.run_id,
            "--report-date",
            args.report_date,
            "--report-suffix",
            args.report_suffix,
            "--routine-stage",
            "routine_fresh_generation_completed_pending_pdf_qa",
            "--workflow-status",
            "routine_fresh_generation_completed_pending_pdf_qa",
            "--previous-delivery-closeout-manifest",
            args.previous_delivery_closeout_manifest,
            "--portfolio-state",
            args.portfolio_state,
            "--valuation-history",
            args.valuation_history,
            "--trade-ledger",
            args.trade_ledger,
            "--recommendation-scorecard",
            args.recommendation_scorecard,
            "--pricing-artifact",
            args.pricing_artifact,
            "--delivery-package-manifest",
            str(manifest_path),
            "--ready-artifact",
            str(ready_path),
            "--dutch-primary-markdown",
            str(nl_md),
            "--english-companion-markdown",
            str(en_md),
            "--dutch-primary-html",
            str(nl_html),
            "--english-companion-html",
            str(en_html),
            "--dutch-primary-pdf",
            str(nl_pdf),
            "--english-companion-pdf",
            str(en_pdf),
            "--next-package",
            "RUN_ROUTINE_PDF_QUALITY_GATES",
        ],
        check=True,
    )
    return {"manifest": manifest_path, "ready": ready_path, "routine": routine_path}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--pricing-artifact", required=True)
    parser.add_argument("--output-dir", default="output/fresh_generation")
    parser.add_argument("--portfolio-state", default="output/etf_eu_portfolio_state.json")
    parser.add_argument("--valuation-history", default="output/etf_eu_valuation_history.csv")
    parser.add_argument("--trade-ledger", default="output/etf_eu_trade_ledger.csv")
    parser.add_argument("--recommendation-scorecard", default="output/etf_eu_recommendation_scorecard.csv")
    parser.add_argument("--previous-routine-manifest", required=True)
    parser.add_argument("--previous-delivery-closeout-manifest", required=True)
    args = parser.parse_args()
    outputs = build(args)
    print("ETF_EU_ROUTINE_REPORT_PACKAGE_OK | " + " | ".join(f"{k}={v}" for k, v in outputs.items()))


if __name__ == "__main__":
    main()
