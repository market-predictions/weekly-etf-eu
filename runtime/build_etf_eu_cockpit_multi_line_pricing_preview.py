from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUN_ID = "20260703_000000"
PRICING = Path("output/client_surface/etf_eu_multi_line_pricing_preview_20260703_000000.json")
MARKDOWN = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.md")
ARTIFACT = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.json")
PDF = Path("output/client_surface/etf_eu_cockpit_multi_line_pricing_preview_20260703_000000.pdf")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| ISIN | Fonds | Handelslijn | Valuta | Slotdatum | Slotkoers | Bron | Status |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        if row["line_status"] != "success":
            continue
        lines.append(
            f"| {row['isin']} | {row['fund_name']} | {row['pricing_symbol']} | {row['trading_currency']} | {row['latest_close_date']} | {row['latest_close']} | {row['pricing_source']} | {row['line_status']} |"
        )
    return "\n".join(lines)


def _pending(rows: list[dict[str, Any]]) -> str:
    pending = [row for row in rows if row["line_status"] != "success"]
    if not pending:
        return "Geen pending regels in deze preview."
    lines = [
        "| ISIN | Fonds | Handelslijn | Status | Reden |",
        "|---|---|---|---|---|",
    ]
    for row in pending:
        lines.append(f"| {row['isin']} | {row['fund_name']} | {row['pricing_symbol']} | {row['line_status']} | {row['line_reason']} |")
    return "\n".join(lines)


def _markdown(data: dict[str, Any]) -> str:
    rows = data["pricing_rows"]
    only_one = data["successful_rows_count"] == 1
    one_line_notice = "\n\nDe multi-line structuur staat klaar, maar alleen SXR8.DE is nu succesvol geprijsd. Extra regels blijven expliciet pending of failed totdat provider- en registry-bewijs slagen." if only_one else ""
    return f"""# ETF EU Cockpit - Multi-line Pricing Preview

## Wat dit nu bewijst

De cockpit kan nu een multi-line pricing structuur tonen zonder U.S. proxyprijzen of handmatige koersen te gebruiken.{one_line_notice}

## Koerstabel - verified EU lines

{_table(rows)}

## Niet opgenomen / nog niet geprijsd

{_pending(rows)}

## Wat dit nog niet bewijst

Dit is een beperkte multi-line koerspreview. Dit is geen waarderingsgeschikte prijsbasis, geen client-grade rapportbewijs en geen leveringsautorisatie.

Het bewijst geen funding, portefeuillemutatie, kandidaatpromotie of productiepad.

## Volgende stap

{data['selected_next_package']} - vervolg afhankelijk van het aantal succesvol geprijsde EU-regels.
"""


def build() -> dict[str, Any]:
    data = _load(PRICING)
    MARKDOWN.write_text(_markdown(data), encoding="utf-8")
    artifact = {
        "schema_version": "etf_eu_cockpit_multi_line_pricing_preview_v1",
        "run_id": RUN_ID,
        "repository": "market-predictions/weekly-etf-eu",
        "work_package_id": "ETF-EU-WP15AA",
        "source_work_package": "ETF-EU-WP15Z",
        "source_multi_line_pricing_artifact": str(PRICING),
        "markdown_preview_path": str(MARKDOWN),
        "pdf_preview_path": str(PDF),
        "pdf_created": PDF.exists(),
        "pdf_reason": "binary_pdf_not_committed_or_not_rendered_in_this_package",
        "preview_surface_created": True,
        "pricing_rows": data["pricing_rows"],
        "successful_rows_count": data["successful_rows_count"],
        "failed_rows_count": data["failed_rows_count"],
        "skipped_rows_count": data["skipped_rows_count"],
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
        "selected_next_package": data["selected_next_package"],
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
