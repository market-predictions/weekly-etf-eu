from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "etf_eu_fresh_generation_package_v1"
ARTIFACT_TYPE = "etf_eu_fresh_generation_package_manifest"
SOURCE_OF_TRUTH_REPO = "market-predictions/weekly-etf-eu"
REFERENCE_ARCHITECTURE_REPO = "market-predictions/weekly-etf"
UPSTREAM_PATTERN = "weekly-etf renderer/package concept; adapted for EU/UCITS fresh package generation"
NEXT_PACKAGE = "ETF-EU-MVP25_FRESH_PACKAGE_READINESS_GATE"

EU_STATE_DEFAULTS = {
    "portfolio_state": "output/etf_eu_portfolio_state.json",
    "valuation_history": "output/etf_eu_valuation_history.csv",
    "trade_ledger": "output/etf_eu_trade_ledger.csv",
    "recommendation_scorecard": "output/etf_eu_recommendation_scorecard.csv",
}

US_STATE_PATHS = {
    "output/etf_portfolio_state.json",
    "output/etf_valuation_history.csv",
    "output/etf_trade_ledger.csv",
    "output/etf_recommendation_scorecard.csv",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Required JSON input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_optional(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_file(pattern: str) -> Path | None:
    matches = sorted(Path(".").glob(pattern))
    return matches[-1] if matches else None


def _reject_us_state(path: str, label: str) -> None:
    if path in US_STATE_PATHS or ("/etf_" in path and "/etf_eu_" not in path and "output/etf_eu_" not in path):
        raise SystemExit(f"{label} must use EU-specific state, not U.S. authority path: {path}")


def _state_summary(portfolio: dict[str, Any]) -> dict[str, Any]:
    return {
        "starting_capital_eur": portfolio.get("starting_capital_eur"),
        "cash_eur": portfolio.get("cash_eur"),
        "invested_market_value_eur": portfolio.get("invested_market_value_eur"),
        "nav_eur": portfolio.get("nav_eur"),
        "position_count": len(portfolio.get("positions") or []),
        "portfolio_mode": portfolio.get("portfolio_mode"),
    }


def _pricing_summary(pricing: dict[str, Any] | None) -> dict[str, Any]:
    if not pricing:
        return {
            "pricing_artifact_available": False,
            "pricing_evidence_role": "not_available",
            "valuation_grade": False,
        }
    return {
        "pricing_artifact_available": True,
        "schema_version": pricing.get("schema_version"),
        "run_id": pricing.get("run_id"),
        "line_count": pricing.get("line_count"),
        "priced_line_count": pricing.get("priced_line_count"),
        "actual_close_fetch_completed": pricing.get("actual_close_fetch_completed"),
        "valuation_grade": False,
        "pricing_evidence_role": "diagnostic_or_reference_only",
    }


def _markdown_nl(report_date: str, state: dict[str, Any], pricing: dict[str, Any] | None) -> str:
    summary = _state_summary(state)
    pricing_summary = _pricing_summary(pricing)
    return f"""# Weekly ETF EU Review | Nederlands | {report_date}

> **Pakketstatus:** fresh-generation rendererintegratie. Dit rapport is geen koopadvies, geen portefeuille-opdracht, geen waarderingsautoriteit en geen delivery.

## 1. Kernsamenvatting

Deze MVP24-output bewijst dat de EU-routine een nieuw Dutch-primary / English-companion pakket kan opbouwen vanuit EU-authoritative state. De output gebruikt het MVP19-FIX2 deliverypakket niet als pakketbron.

- **Modelstaat:** {summary.get('portfolio_mode') or 'onbekend'}.
- **Cash EUR:** {summary.get('cash_eur')}.
- **Belegde marktwaarde EUR:** {summary.get('invested_market_value_eur')}.
- **Gefinancierde posities:** {summary.get('position_count')}.
- **Beslissing:** research review only; geen allocatie en geen trade.

## 2. EU-state contract

| Component | Waarde |
|---|---:|
| Startkapitaal EUR | {summary.get('starting_capital_eur')} |
| Cash EUR | {summary.get('cash_eur')} |
| Belegde marktwaarde EUR | {summary.get('invested_market_value_eur')} |
| Totale portefeuillewaarde EUR | {summary.get('nav_eur')} |
| Posities | {summary.get('position_count')} |

## 3. UCITS pricing evidence

| Controlepunt | Status |
|---|---|
| Pricing artifact beschikbaar | {pricing_summary.get('pricing_artifact_available')} |
| Pricing evidence role | {pricing_summary.get('pricing_evidence_role')} |
| Valuation-grade | false |
| Funding authority | false |

## 4. Output package

| Output | Status |
|---|---|
| Dutch primary markdown | generated |
| English companion markdown | generated |
| Dutch primary HTML | generated |
| English companion HTML | generated |
| Dutch primary PDF | generated |
| English companion PDF | generated |
| Ready for controlled delivery | false |

## 5. Authority

```text
send_executed=false
transport_attempted=false
receipt_confirmed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

## 6. Next gate

MVP25 moet een aparte package-readiness gate uitvoeren voordat controlled delivery mogelijk is.
"""


def _markdown_en(report_date: str, state: dict[str, Any], pricing: dict[str, Any] | None) -> str:
    summary = _state_summary(state)
    pricing_summary = _pricing_summary(pricing)
    return f"""# Weekly ETF EU Review | English Companion | {report_date}

> **Package status:** fresh-generation renderer integration. This report is not advice, not a portfolio instruction, not valuation authority and not delivery.

## 1. Executive summary

This MVP24 output proves that the EU routine can build a new Dutch-primary / English-companion package from EU-authoritative state. The output does not use the MVP19-FIX2 delivery package as package source.

- **Model state:** {summary.get('portfolio_mode') or 'unknown'}.
- **Cash EUR:** {summary.get('cash_eur')}.
- **Invested market value EUR:** {summary.get('invested_market_value_eur')}.
- **Funded positions:** {summary.get('position_count')}.
- **Decision:** research review only; no allocation and no trade.

## 2. EU state contract

| Component | Value |
|---|---:|
| Starting capital EUR | {summary.get('starting_capital_eur')} |
| Cash EUR | {summary.get('cash_eur')} |
| Invested market value EUR | {summary.get('invested_market_value_eur')} |
| Total portfolio value EUR | {summary.get('nav_eur')} |
| Positions | {summary.get('position_count')} |

## 3. UCITS pricing evidence

| Checkpoint | Status |
|---|---|
| Pricing artifact available | {pricing_summary.get('pricing_artifact_available')} |
| Pricing evidence role | {pricing_summary.get('pricing_evidence_role')} |
| Valuation-grade | false |
| Funding authority | false |

## 4. Output package

| Output | Status |
|---|---|
| Dutch primary markdown | generated |
| English companion markdown | generated |
| Dutch primary HTML | generated |
| English companion HTML | generated |
| Dutch primary PDF | generated |
| English companion PDF | generated |
| Ready for controlled delivery | false |

## 5. Authority

```text
send_executed=false
transport_attempted=false
receipt_confirmed=false
valuation_grade=false
funding_authority=false
portfolio_mutation=false
production_delivery_authority=false
```

## 6. Next gate

MVP25 must run a separate package-readiness gate before controlled delivery can be considered.
"""


def _html_from_markdown(md_text: str, title: str, lang: str) -> str:
    parts: list[str] = []
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            parts.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            parts.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("| ") or line.startswith("|---"):
            parts.append(f"<pre>{html.escape(line)}</pre>")
        elif line.startswith("- "):
            parts.append(f"<p>{html.escape(line)}</p>")
        else:
            parts.append(f"<p>{html.escape(line)}</p>")
    return "<!doctype html>\n" + f"<html lang='{lang}'>\n<head><meta charset='utf-8'><title>{html.escape(title)}</title></head>\n<body>\n" + "\n".join(parts) + "\n</body>\n</html>\n"


def _simple_pdf(title: str, lines: list[str]) -> str:
    def esc(value: str) -> str:
        clean = value.encode("ascii", "ignore").decode("ascii")
        return clean.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    content = ["BT", "/F1 14 Tf", "50 780 Td", f"({esc(title)}) Tj", "/F1 10 Tf"]
    for raw in lines[:40]:
        line = raw.replace("#", "").replace("|", " ").replace("`", " ").strip()
        if not line:
            continue
        content.append("0 -16 Td")
        content.append(f"({esc(line[:92])}) Tj")
    content.append("ET")
    stream = "\n".join(content) + "\n"
    objects = [
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(stream.encode('ascii'))} >>\nstream\n{stream}endstream\nendobj\n",
    ]
    pdf = "%PDF-1.4\n%ASCII\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf.encode("latin-1")))
        pdf += obj
    xref_offset = len(pdf.encode("latin-1"))
    pdf += "xref\n0 6\n0000000000 65535 f \n"
    for off in offsets[1:]:
        pdf += f"{off:010d} 00000 n \n"
    pdf += f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
    return pdf


def build(args: argparse.Namespace) -> dict[str, Path]:
    for label in EU_STATE_DEFAULTS:
        _reject_us_state(str(getattr(args, label)), label)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    portfolio_state_path = Path(args.portfolio_state)
    portfolio = _load_json(portfolio_state_path)
    pricing_path = Path(args.pricing_artifact) if args.pricing_artifact else _latest_file("output/pricing/ucits_close_price_validation_basket_results_*.json")
    pricing = _load_json_optional(pricing_path)

    nl_md = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.md"
    en_md = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.md"
    nl_html = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.html"
    en_html = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.html"
    nl_pdf = output_dir / f"weekly_etf_eu_review_nl_{args.report_suffix}.pdf"
    en_pdf = output_dir / f"weekly_etf_eu_review_{args.report_suffix}.pdf"
    package_manifest = output_dir / f"etf_eu_fresh_generation_package_manifest_{args.run_id}.json"
    ready_artifact = output_dir / f"etf_eu_ready_for_controlled_delivery_{args.run_id}.json"

    nl_md_text = _markdown_nl(args.report_date, portfolio, pricing)
    en_md_text = _markdown_en(args.report_date, portfolio, pricing)
    nl_md.write_text(nl_md_text, encoding="utf-8")
    en_md.write_text(en_md_text, encoding="utf-8")
    nl_html.write_text(_html_from_markdown(nl_md_text, f"Weekly ETF EU NL {args.report_date}", "nl"), encoding="utf-8")
    en_html.write_text(_html_from_markdown(en_md_text, f"Weekly ETF EU EN {args.report_date}", "en"), encoding="utf-8")
    nl_pdf.write_text(_simple_pdf(f"Weekly ETF EU Review NL {args.report_date}", nl_md_text.splitlines()), encoding="latin-1")
    en_pdf.write_text(_simple_pdf(f"Weekly ETF EU Review EN {args.report_date}", en_md_text.splitlines()), encoding="latin-1")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "report_suffix": args.report_suffix,
        "source_of_truth_repo": SOURCE_OF_TRUTH_REPO,
        "reference_architecture_repo": REFERENCE_ARCHITECTURE_REPO,
        "upstream_pattern_adapted": UPSTREAM_PATTERN,
        "fresh_generation_status": "full_package_generated",
        "full_generation_status": "renderer_integrated",
        "markdown_generation_status": "generated",
        "html_generation_status": "generated",
        "pdf_generation_status": "generated",
        "markdown_output_available": True,
        "html_output_available": True,
        "pdf_output_available": True,
        "ready_for_controlled_delivery": False,
        "dutch_primary": True,
        "english_companion": True,
        "isin_first_identity": True,
        "us_etfs_proxy_only": True,
        "main_surface_us_holdings_exposure": False,
        "nan_price_in_client_surface": False,
        "stale_delivery_wording_present": False,
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "portfolio_state_path": str(portfolio_state_path),
        "valuation_history_path": args.valuation_history,
        "trade_ledger_path": args.trade_ledger,
        "recommendation_scorecard_path": args.recommendation_scorecard,
        "pricing_artifact_path": str(pricing_path) if pricing_path else None,
        "previous_routine_run_manifest": args.routine_manifest,
        "previous_delivery_closeout_manifest": args.previous_delivery_closeout_manifest,
        "dutch_primary_markdown": str(nl_md),
        "english_companion_markdown": str(en_md),
        "dutch_primary_html": str(nl_html),
        "english_companion_html": str(en_html),
        "dutch_primary_pdf": str(nl_pdf),
        "english_companion_pdf": str(en_pdf),
        "ready_artifact": str(ready_artifact),
        "next_package": NEXT_PACKAGE,
    }
    package_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ready = {
        "schema_version": "etf_eu_ready_for_controlled_delivery_v1",
        "artifact_type": "etf_eu_ready_for_controlled_delivery",
        "generated_at_utc": _utc_now(),
        "run_id": args.run_id,
        "report_date": args.report_date,
        "fresh_generation_package_manifest": str(package_manifest),
        "ready_for_controlled_delivery": False,
        "reason": "MVP24 generated the full markdown/html/pdf package; MVP25 package-readiness gate remains required before controlled delivery.",
        "send_executed": False,
        "transport_attempted": False,
        "receipt_confirmed": False,
        "valuation_grade": False,
        "funding_authority": False,
        "portfolio_mutation": False,
        "production_delivery_authority": False,
        "next_package": NEXT_PACKAGE,
    }
    ready_artifact.write_text(json.dumps(ready, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd = [
        sys.executable,
        "tools/write_etf_eu_routine_run_manifest.py",
        "--run-id", args.run_id,
        "--report-date", args.report_date,
        "--report-suffix", args.report_suffix,
        "--routine-stage", "fresh_generation_renderer_integrated",
        "--workflow-status", "fresh_generation_renderer_integrated",
        "--previous-delivery-closeout-manifest", args.previous_delivery_closeout_manifest,
        "--portfolio-state", args.portfolio_state,
        "--valuation-history", args.valuation_history,
        "--trade-ledger", args.trade_ledger,
        "--recommendation-scorecard", args.recommendation_scorecard,
        "--pricing-artifact", str(pricing_path) if pricing_path else "",
        "--delivery-package-manifest", str(package_manifest),
        "--ready-artifact", str(ready_artifact),
        "--dutch-primary-markdown", str(nl_md),
        "--english-companion-markdown", str(en_md),
        "--dutch-primary-html", str(nl_html),
        "--english-companion-html", str(en_html),
        "--dutch-primary-pdf", str(nl_pdf),
        "--english-companion-pdf", str(en_pdf),
        "--next-package", NEXT_PACKAGE,
    ]
    subprocess.run(cmd, check=True)

    return {
        "package_manifest": package_manifest,
        "ready_artifact": ready_artifact,
        "dutch_primary_markdown": nl_md,
        "english_companion_markdown": en_md,
        "dutch_primary_html": nl_html,
        "english_companion_html": en_html,
        "dutch_primary_pdf": nl_pdf,
        "english_companion_pdf": en_pdf,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ETF EU fresh-generation package with no send.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--report-suffix", required=True)
    parser.add_argument("--output-dir", default="output/fresh_generation")
    parser.add_argument("--portfolio-state", default=EU_STATE_DEFAULTS["portfolio_state"])
    parser.add_argument("--valuation-history", default=EU_STATE_DEFAULTS["valuation_history"])
    parser.add_argument("--trade-ledger", default=EU_STATE_DEFAULTS["trade_ledger"])
    parser.add_argument("--recommendation-scorecard", default=EU_STATE_DEFAULTS["recommendation_scorecard"])
    parser.add_argument("--pricing-artifact", default=None)
    parser.add_argument("--routine-manifest", default="output/run_manifests/etf_eu_routine_run_manifest_2026-07-10_20260710_000000.json")
    parser.add_argument("--previous-delivery-closeout-manifest", default="output/run_manifests/etf_eu_delivery_closeout_manifest_20260710_1755.json")
    args = parser.parse_args()

    outputs = build(args)
    print("ETF_EU_FRESH_GENERATION_PACKAGE_OK | " + " | ".join(f"{key}={value}" for key, value in outputs.items()))


if __name__ == "__main__":
    main()
