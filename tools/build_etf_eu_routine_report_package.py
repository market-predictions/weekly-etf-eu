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
    candidates: list[str] = []
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

## 7. Volgende routineactie

- Rond verificatie van brokerbeschikbaarheid en EUR-handelslijnen af.
- Voeg waar beschikbaar onafhankelijke prijsverificatie toe; het tijdelijk ontbreken van een tweede actuele verifier blokkeert een exact aan de geverifieerde handelslijn gekoppelde slotkoers niet.
- Herbeoordeel portefeuille- of cashinzet alleen vanuit het afzonderlijke allocatie- en re-underwritingkader.
"""


def _markdown_en(report_date: str, state: dict[str, Any], pricing: dict[str, Any]) -> str:
    rows = _pricing_rows(pricing)
    latest = _latest_close_date(rows) or "unavailable"
    return f"""# Weekly ETF EU Review | English Companion | {report_date}

> **Routine production review.** Pricing date: {latest}. The EU portfolio remains ISIN-first. U.S. ETF symbols are research references only and are not investable in this model.

## 1. Decision at a glance

- **Action:** no trade; retain EUR 100,000 cash.
- **Reason:** the portfolio still has no funded UCITS positions and the current pricing run provides market observations, not an independent basis for purchase or valuation.
- **Most advanced operational candidate:** the verified S&P 500 UCITS lines remain furthest advanced for broker and trading-line confirmation.
- **Avoid:** do not allocate capital to thematic or gold exposure until identity, KID, trading-line and product-policy checks are complete.

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

The displayed prices are market observations from the current routine run and do not independently authorize valuation or purchase.

## 4. Coverage and decision quality

{_lane_summary(rows, dutch=False)}

## 5. Lane assessment

- **Core equity:** operationally most mature; SXR8 and CSPX remain research candidates and are not funded.
- **Global equity:** IWDA, EUNL and VWCE remain relevant for broad diversification, but trading-line and source verification is incomplete.
- **Technology and semiconductors:** SXRV, CNDX and SMH carry higher beta and concentration risk; no capital allocation before full verification.
- **Bonds:** EUNA and AGGH may later provide stability; their current role remains that of research candidates.
- **Gold:** European exposure often uses ETC structures and remains blocked under the UCITS-only policy until an explicit policy decision exists.

## 6. Risk and quality boundaries

1. A price observation is not an independent valuation basis.
2. A ticker is not canonical identity; ISIN remains authoritative.
3. No portfolio change without a separate capital-allocation decision.
4. Previous reports are historical strategy context, not current-price truth.
5. Unresolved lines remain outside the client decision.

## 7. Next routine action

- Complete broker availability and EUR trading-line verification.
- Add independent price verification where available; temporary absence of a second current verifier does not block an exact close bound to the verified trading line.
- Reassess portfolio or cash deployment only through the separate allocation and re-underwriting framework.
"""


def _validate_canonical_pricing(args: argparse.Namespace) -> dict[str, Any]:
    result = validate_v2_pricing(
        Path(args.pricing_artifact),
        expected_report_date=args.report_date,
        portfolio_state_path=Path(args.portfolio_state),
        require_funded_consensus=True,
    )
    if result["valid"] is not True:
        raise SystemExit("Canonical v2 pricing contract failed for package generation: " + "; ".join(result["blockers"]))
    return result


def build(args: argparse.Namespace) -> dict[str, Path]:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    state = _load_json(Path(args.portfolio_state))
    pricing = _load_json(Path(args.pricing_artifact))
    pricing_validation = _validate_canonical_pricing(args)
    rows = _pricing_rows(pricing)

    nl_md = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.md"
    en_md = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.md"
    nl_html = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.html"
    en_html = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.html"
    nl_pdf = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.pdf"
    en_pdf = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.pdf"
    manifest_path = output_dir / f"etf_eu_fresh_generation_package_manifest_{args.run_id}.json"
    ready_path = output_dir / f"etf_eu_ready_for_controlled_delivery_{args.run_id}.json"
    routine_path = Path("output/run_manifests") / f"etf_eu_routine_run_manifest_{args.report_date}_{args.run_id}.json"

    nl_text, nl_sanitization = sanitize_text(_markdown_nl(args.report_date, state, pricing), language="nl")
    en_text, en_sanitization = sanitize_text(_markdown_en(args.report_date, state, pricing), language="en")
    if nl_sanitization["client_surface_sanitized"] is not True or en_sanitization["client_surface_sanitized"] is not True:
        raise SystemExit("Native client-surface sanitization guard failed")
    nl_md.write_text(nl_text, encoding="utf-8")
    en_md.write_text(en_text, encoding="utf-8")

    render_report(markdown_path=nl_md, html_output=nl_html, pdf_output=nl_pdf, language="nl", title=f"Weekly ETF EU Review | Nederlands | {args.report_date}")
    render_report(markdown_path=en_md, html_output=en_html, pdf_output=en_pdf, language="en", title=f"Weekly ETF EU Review | English Companion | {args.report_date}")

    latest_close = _latest_close_date(rows)
    pricing_policy = pricing.get("pricing_authority_policy") or {}
    manifest = {
        "schema_version": "etf_eu_fresh_generation_package_v1",
        "artifact_type": "etf_eu_fresh_generation_package_manifest",
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "pricing_as_of": latest_close,
        "pricing_contract_schema": "ucits_close_price_validation_basket_results_v2",
        "pricing_contract_validation": pricing_validation,
        "funded_exact_primary_pricing_required": True,
        "second_provider_required_for_liveness": pricing_policy.get("second_provider_required_for_liveness") is True,
        "funded_two_provider_consensus_required": False,
        "pricing_authority_mode": pricing_policy.get("mode"),
        "source_of_truth_repo": SOURCE_REPO,
        "reference_architecture_repo": DONOR_REPO,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "fresh_generation_status": "full_package_generated",
        "full_generation_status": "client_grade_renderer_integrated",
        "markdown_generation_status": "generated_client_safe",
        "html_generation_status": "generated",
        "pdf_generation_status": "generated_pending_quality_gates",
        "renderer": "runtime/render_etf_eu_client_report.py",
        "renderer_engine": "weasyprint",
        "markdown_engine": "mistune_table",
        "client_surface_sanitizer": "runtime/scrub_etf_eu_client_surface.py",
        "client_surface_sanitized": True,
        "authority_metadata_absent_from_client_surface": True,
        "raw_status_enums_absent_from_client_surface": True,
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
        "valuation_grade": pricing_validation["report_pricing_gate_passed"],
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
        "next_action": "RUN_ROUTINE_CLIENT_SURFACE_AND_PDF_QUALITY_GATES",
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
        "pricing_contract_schema": "ucits_close_price_validation_basket_results_v2",
        "funded_exact_primary_pricing_required": True,
        "second_provider_required_for_liveness": pricing_policy.get("second_provider_required_for_liveness") is True,
        "funded_two_provider_consensus_required": False,
        "pricing_authority_mode": pricing_policy.get("mode"),
        "client_surface_clean": False,
        "authority_metadata_absent": False,
        "raw_status_enums_absent": False,
        "pdf_machine_gate_passed": False,
        "pdf_visual_gate_passed": False,
        "client_output_valid": False,
        "ready_for_controlled_delivery": False,
        "delivery_authorized": False,
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": pricing_validation["report_pricing_gate_passed"],
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "next_action": "RUN_ROUTINE_CLIENT_SURFACE_AND_PDF_QUALITY_GATES",
    }
    ready_path.write_text(json.dumps(ready, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            "tools/write_etf_eu_routine_run_manifest.py",
            "--run-id", args.run_id,
            "--report-date", args.report_date,
            "--report-suffix", args.report_suffix,
            "--routine-stage", "routine_fresh_generation_completed_pending_client_surface_and_pdf_qa",
            "--workflow-status", "routine_fresh_generation_completed_pending_client_surface_and_pdf_qa",
            "--previous-delivery-closeout-manifest", args.previous_delivery_closeout_manifest,
            "--portfolio-state", args.portfolio_state,
            "--valuation-history", args.valuation_history,
            "--trade-ledger", args.trade_ledger,
            "--recommendation-scorecard", args.recommendation_scorecard,
            "--pricing-artifact", args.pricing_artifact,
            "--delivery-package-manifest", str(manifest_path),
            "--ready-artifact", str(ready_path),
            "--dutch-primary-markdown", str(nl_md),
            "--english-companion-markdown", str(en_md),
            "--dutch-primary-html", str(nl_html),
            "--english-companion-html", str(en_html),
            "--dutch-primary-pdf", str(nl_pdf),
            "--english-companion-pdf", str(en_pdf),
            "--next-package", "RUN_ROUTINE_CLIENT_SURFACE_AND_PDF_QUALITY_GATES",
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
    print("ETF_EU_ROUTINE_REPORT_PACKAGE_OK | " + " | ".join(f"{key}={value}" for key, value in outputs.items()))


if __name__ == "__main__":
    main()
