from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def preferred_variant(allocator: dict[str, Any]) -> dict[str, Any]:
    preferred = str(allocator.get("preferred_shadow_variant") or "staged_policy_driven_v1")
    for variant in allocator.get("variants") or []:
        if isinstance(variant, dict) and variant.get("variant_id") == preferred:
            return variant
    raise RuntimeError(f"Preferred variant missing: {preferred}")


def euro(value: Any, language: str, decimals: int = 2) -> str:
    amount = float(value or 0)
    rendered = f"{amount:,.{decimals}f}"
    if language == "nl":
        rendered = rendered.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {rendered}"


def pct(value: Any, language: str) -> str:
    rendered = f"{float(value or 0):.2f}%"
    return rendered.replace(".", ",") if language == "nl" else rendered


def compact_box(
    html_path: Path,
    pdf_path: Path,
    *,
    variant: dict[str, Any],
    language: str,
) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    existing = soup.find(class_="shadow-expansion-proposal")
    if not isinstance(existing, Tag):
        raise RuntimeError(f"Expansion proposal missing: {html_path}")

    rows = [
        row
        for row in variant.get("allocation_rows") or []
        if isinstance(row, dict) and row.get("selected") is True and row.get("eligible") is True
    ]
    if len(rows) != 2:
        raise RuntimeError(f"Expected exactly two selected expansion rows, found {len(rows)}")

    box = soup.new_tag("div", attrs={"class": "model-expansion-proposal compact"})
    heading = soup.new_tag("strong")
    heading.string = (
        "Modelvoorstel: uitbreiding naar vijf posities — niet geactiveerd"
        if language == "nl"
        else "Model proposal: expansion to five positions — not activated"
    )
    box.append(heading)

    for row in rows:
        candidate = row.get("candidate") or {}
        order = row.get("order") or {}
        ticker = "L0CK" if candidate.get("ticker") == "LOCK" else str(candidate.get("ticker") or "—")
        shares = int(order.get("target_shares") or 0)
        close = float(candidate.get("price_eur") or 0)
        decimals = 4 if close < 20 else 2
        line = soup.new_tag("div", attrs={"class": "model-proposal-line"})
        if language == "nl":
            line.string = (
                f"{ticker}: koopvoorstel {shares} stuks @ {euro(close, language, decimals)}; "
                f"doel {pct(row.get('variant_target_weight_pct'), language)}; "
                f"bruto {euro(order.get('gross_trade_value_eur'), language)}; niet uitgevoerd."
            )
        else:
            line.string = (
                f"{ticker}: proposed buy {shares} shares @ {euro(close, language, decimals)}; "
                f"target {pct(row.get('variant_target_weight_pct'), language)}; "
                f"gross {euro(order.get('gross_trade_value_eur'), language)}; not executed."
            )
        box.append(line)

    summary = variant.get("summary") or {}
    footer = soup.new_tag("div", attrs={"class": "model-proposal-footer"})
    if language == "nl":
        footer.string = (
            f"Projectie na activatie: {int(summary.get('position_count') or 0)} posities; "
            f"cash {euro(summary.get('projected_cash_eur'), language)} "
            f"({pct(summary.get('projected_cash_weight_pct'), language)}). "
            "Officiële stukken, cash en ledger blijven ongewijzigd."
        )
    else:
        footer.string = (
            f"Projection after activation: {int(summary.get('position_count') or 0)} positions; "
            f"cash {euro(summary.get('projected_cash_eur'), language)} "
            f"({pct(summary.get('projected_cash_weight_pct'), language)}). "
            "Official shares, cash and ledger remain unchanged."
        )
    box.append(footer)
    existing.replace_with(box)

    style = soup.new_tag("style")
    style.string = """
.model-expansion-proposal.compact{margin:.28rem 0 0;padding:.34rem .48rem;border:1px solid #9fb6c7;border-radius:6px;background:#f3f7fa;font-size:7.35pt;line-height:1.16;break-inside:avoid}
.model-proposal-line{margin:.14rem 0;font-variant-numeric:tabular-nums}
.model-proposal-footer{margin-top:.18rem;font-weight:600}
"""
    soup.head.append(style)
    html_path.write_text(str(soup), encoding="utf-8")
    HTML(filename=str(html_path), base_url=str(html_path.parent.resolve())).write_pdf(str(pdf_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument(
        "--allocator",
        type=Path,
        default=Path("output/routine_preview/sync/etf_eu_target_allocator_shadow.json"),
    )
    args = parser.parse_args()

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "runtime/add_etf_eu_expanded_allocation_monitor_v2.py"),
            str(args.manifest),
            "--pricing",
            str(args.pricing),
            "--report-date",
            args.report_date,
            "--allocator",
            str(args.allocator),
        ],
        cwd=str(ROOT),
        check=True,
    )

    manifest = load_object(args.manifest)
    variant = preferred_variant(load_object(args.allocator))
    for language in ("nl", "en"):
        record = manifest.get("languages", {}).get(language, {})
        compact_box(
            Path(record["html"]),
            Path(record["pdf"]),
            variant=variant,
            language=language,
        )
        record["expanded_model_proposal_surface"] = "compact_two_line_v1"
    manifest["expanded_model_proposal_surface"] = {
        "applied": True,
        "format": "compact_two_line_v1",
        "selected_candidate_count": 2,
        "portfolio_mutation": False,
        "real_broker_execution": False,
        "activation_authority": False,
    }
    args.manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("ETF_EU_COMPACT_MODEL_PROPOSAL_OK | candidates=2 | official_state_applied=false")


if __name__ == "__main__":
    main()
